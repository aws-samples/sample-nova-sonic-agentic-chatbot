from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from nova_sonic_simple import SimpleNovaSonic, CHUNK_SIZE
import logging
import os
import wave
from datetime import datetime
import uuid
import json
import time
from api.apps import routers as app_routers

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create debug directory if it doesn't exist
DEBUG_DIR = "debug_audio"
os.makedirs(DEBUG_DIR, exist_ok=True)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self, save_debug_audio=True):
        self.nova_client = None
        self.active_connection = None
        self.audio_content_started = False
        self.debug_input_file = None
        self.debug_output_file = None
        self.received_chunks = 0
        self.sent_chunks = 0
        self.current_content_name = None
        self.current_tool_use_id = None
        self.current_tool_name = None
        self.last_audio_chunk_time = 0  # Track timing of audio chunks
        self.audio_chunk_threshold = 0.1  # 100ms threshold for audio chunks
        self.save_debug_audio = save_debug_audio  # <--- New config option
        # --- Chat history ---
        self.chat_history = []  # List of dicts: {role, text, contentName}
        self.max_history = 10   # Rolling window size

    def add_history(self, role, text):
        """Add a message to the rolling chat history."""
        content_name = str(uuid.uuid4())
        self.chat_history.append({
            'role': role,
            'text': text,
            'contentName': content_name
        })
        # Keep only the last N messages
        if len(self.chat_history) > self.max_history:
            self.chat_history = self.chat_history[-self.max_history:]

    def get_history(self):
        """Get the current rolling chat history."""
        return self.chat_history.copy()

    def _create_debug_files(self):
        if not self.save_debug_audio:
            self.debug_input_file = None
            self.debug_output_file = None
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_path = os.path.join(DEBUG_DIR, f"input_{timestamp}.wav")
        output_path = os.path.join(DEBUG_DIR, f"output_{timestamp}.wav")

        # Create WAV file for input audio (16kHz)
        self.debug_input_file = wave.open(input_path, 'wb')
        self.debug_input_file.setnchannels(1)
        self.debug_input_file.setsampwidth(2)  # 16-bit
        self.debug_input_file.setframerate(16000)
        
        # Create WAV file for output audio (24kHz)
        self.debug_output_file = wave.open(output_path, 'wb')
        self.debug_output_file.setnchannels(1)
        self.debug_output_file.setsampwidth(2)  # 16-bit
        self.debug_output_file.setframerate(24000)

        logger.info(f"Created debug files: {input_path} and {output_path}")

    def _close_debug_files(self):
        if not self.save_debug_audio:
            self.debug_input_file = None
            self.debug_output_file = None
            return
        if self.debug_input_file:
            self.debug_input_file.close()
            self.debug_input_file = None
        if self.debug_output_file:
            self.debug_output_file.close()
            self.debug_output_file = None
        logger.info(f"Debug stats - Received chunks: {self.received_chunks}, Sent chunks: {self.sent_chunks}")
        self.received_chunks = 0
        self.sent_chunks = 0

    async def process_tool_use(self, tool_name, tool_use_content):
        """Process tool use requests and return results"""
        logger.info(f"Processing tool use: {tool_name}")
        
        try:
            # Use the tool manager to execute the tool
            result = await self.nova_client.tool_manager.execute_tool(tool_name, tool_use_content)
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": f"Tool execution failed: {str(e)}"}

    async def handle_tool_use(self, event_data):
        """Handle tool use events"""
        try:
            tool_use = event_data["event"]["toolUse"]
            self.current_tool_use_id = tool_use["toolUseId"]
            self.current_tool_name = tool_use.get("toolName")
            tool_content = json.loads(tool_use.get("content", "{}"))
            
            # Process the tool use
            result = await self.process_tool_use(self.current_tool_name, tool_content)
            logger.info(f"Tool result received from implementation: {result}")
            
            if "error" not in result:
                # First send the model result
                tool_result = {
                    "event": {
                        "toolResult": {
                            "promptName": tool_use["promptName"],
                            "contentName": str(uuid.uuid4()),
                            "content": json.dumps(result["model_result"])
                        }
                    }
                }
                
                # Then prepare and send the UI result separately
                if "ui_result" in result:
                    tool_ui_result = {
                        "event": {
                            "toolUiOutput": result["ui_result"]
                        }
                    }
                
                if self.active_connection:
                    # Send model result first
                    logger.info("Sending model result")
                    await self.active_connection.send_text(json.dumps(tool_result))
                    
                    # Then send UI result if available
                    if "ui_result" in result:
                        logger.info(f"Sending UI result: {tool_ui_result}")
                        await self.active_connection.send_text(json.dumps(tool_ui_result))
                        logger.info("UI result sent")
            else:
                # Handle error case
                error_result = {
                    "event": {
                        "toolResult": {
                            "promptName": tool_use["promptName"],
                            "contentName": str(uuid.uuid4()),
                            "content": json.dumps(result)
                        }
                    }
                }
                if self.active_connection:
                    await self.active_connection.send_text(json.dumps(error_result))
                
        except Exception as e:
            logger.error(f"Error handling tool use: {e}")
            error_result = {
                "event": {
                    "toolResult": {
                        "promptName": tool_use["promptName"] if "toolUse" in event_data["event"] else str(uuid.uuid4()),
                        "contentName": str(uuid.uuid4()),
                        "content": json.dumps({"error": str(e)})
                    }
                }
            }
            if self.active_connection:
                await self.active_connection.send_text(json.dumps(error_result))

    async def connect(self, websocket: WebSocket, model_id: str = "amazon.nova-sonic-v1:0", language: str = "en"):
        await websocket.accept()
        self.active_connection = websocket
        logger.info(f"WebSocket connection accepted with model: {model_id}, language: {language}")
        
        self.nova_client = SimpleNovaSonic(model_id=model_id, language=language)
        await self.nova_client.start_session()
        logger.info(f"Nova Sonic session started with model: {model_id}, language: {language}")

        # --- Send conversation history after system prompt ---
        history = self.get_history()
        # Only include history starting with a USER message
        while history and history[0]['role'] != 'USER':
            history.pop(0)
        if history:
            for msg in history:
                content_name = msg['contentName']
                role = msg['role']
                text = msg['text']
                # Send contentStart
                content_start = {
                    "event": {
                        "contentStart": {
                            "promptName": self.nova_client.prompt_name,
                            "contentName": content_name,
                            "type": "TEXT",
                            "interactive": False,
                            "role": role,
                            "textInputConfiguration": {
                                "mediaType": "text/plain"
                            }
                        }
                    }
                }
                await self.nova_client.send_event(json.dumps(content_start))
                # Send textInput
                text_input = {
                    "event": {
                        "textInput": {
                            "promptName": self.nova_client.prompt_name,
                            "contentName": content_name,
                            "content": text
                        }
                    }
                }
                await self.nova_client.send_event(json.dumps(text_input))
                # Send contentEnd
                content_end = {
                    "event": {
                        "contentEnd": {
                            "promptName": self.nova_client.prompt_name,
                            "contentName": content_name
                        }
                    }
                }
                await self.nova_client.send_event(json.dumps(content_end))

    async def disconnect(self):
        if self.nova_client:
            logger.info("Stopping Nova Sonic session")
            if self.audio_content_started:
                await self.stop_audio()
            self.nova_client.is_active = False
            await self.nova_client.end_session()
            self.nova_client = None
        self._close_debug_files()
        self.active_connection = None

    async def receive_audio(self, audio_data: bytes):
        if self.nova_client and self.audio_content_started:
            try:
                current_time = time.time()
                time_since_last_chunk = current_time - self.last_audio_chunk_time
                
                # Only process audio if enough time has passed (prevent overwhelming the system)
                if time_since_last_chunk >= self.audio_chunk_threshold:
                    # Save input audio to debug file
                    if self.save_debug_audio and self.debug_input_file:
                        self.debug_input_file.writeframes(audio_data)
                        self.received_chunks += 1
                        if self.received_chunks % 100 == 0:
                            logger.info(f"Received {self.received_chunks} audio chunks")

                    # Send to Nova Sonic
                    await self.nova_client.send_audio_chunk(audio_data)
                    self.last_audio_chunk_time = current_time
                    logger.debug(f"Sent audio chunk of size {len(audio_data)} bytes")
            except Exception as e:
                logger.error(f"Error sending audio chunk: {e}")

    async def start_audio(self):
        if self.nova_client and not self.audio_content_started:
            try:
                logger.info("Starting audio input")
                self._create_debug_files()  # Create new debug files for this session
                
                # Generate new unique content name
                self.current_content_name = str(uuid.uuid4())
                logger.info(f"Using new content name: {self.current_content_name}")
                
                # Start audio with new content name
                self.nova_client.audio_content_name = self.current_content_name
                await self.nova_client.start_audio_input()
                self.audio_content_started = True
            except Exception as e:
                logger.error(f"Error starting audio input: {e}")

    async def stop_audio(self):
        if self.nova_client and self.audio_content_started:
            try:
                logger.info("Stopping audio input")
                await self.nova_client.end_audio_input()
                self.audio_content_started = False
                self.current_content_name = None
                self._close_debug_files()  # Close debug files when stopping
            except Exception as e:
                logger.error(f"Error stopping audio input: {e}")

    async def process_audio_responses(self):
        if not self.nova_client or not self.active_connection:
            return

        logger.info("Started processing audio responses")
        try:
            while self.nova_client.is_active:
                try:
                    # Use timeout to allow checking barge-in status
                    audio_data = await asyncio.wait_for(
                        self.nova_client.audio_queue.get(),
                        timeout=0.1
                    )
                    
                    if audio_data:
                        # Check if we're in a barge-in state
                        if self.nova_client.barge_in:
                            logger.info("Barge-in detected, skipping audio output")
                            continue

                        # Save output audio to debug file
                        if self.save_debug_audio and self.debug_output_file:
                            self.debug_output_file.writeframes(audio_data)
                            self.sent_chunks += 1
                            if self.sent_chunks % 10 == 0:
                                logger.info(f"Sent {self.sent_chunks} response chunks")

                        # Send audio in smaller chunks for better responsiveness
                        for i in range(0, len(audio_data), CHUNK_SIZE):
                            if self.nova_client.barge_in:
                                break
                            chunk = audio_data[i:min(i + CHUNK_SIZE, len(audio_data))]
                            await self.active_connection.send_bytes(chunk)
                            await asyncio.sleep(0.001)  # Small yield

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing audio response: {e}")
                    await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Error in audio response processing loop: {e}")
        finally:
            logger.info("Stopped processing audio responses")

    async def process_events(self):
        if not self.nova_client or not self.active_connection:
            return
        try:
            while self.nova_client.is_active:
                try:
                    event_json = await asyncio.wait_for(
                        self.nova_client.event_queue.get(),
                        timeout=1.0
                    )
                    if event_json:
                        # Check for barge-in before sending events
                        event_data = json.loads(event_json)
                        if 'event' in event_data and 'textOutput' in event_data['event']:
                            text_content = event_data['event']['textOutput'].get('content', '')
                            # Add assistant message to history
                            self.add_history('ASSISTANT', text_content)
                            if '{ "interrupted" : true }' in text_content:
                                logger.info("Barge-in detected in event processing")
                                self.nova_client.barge_in = True
                                
                                # Send barge-in event to frontend
                                barge_in_event = {
                                    "event": {
                                        "toolUiOutput": {
                                            "type": "barge_in",
                                            "content": {
                                                "status": "interrupted"
                                            }
                                        }
                                    }
                                }
                                await self.active_connection.send_text(json.dumps(barge_in_event))
                                
                        await self.active_connection.send_text(event_json)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing event: {e}")
                    await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Error in event processing loop: {e}")
        finally:
            logger.info("Stopped processing events")

    async def handle_ui_interaction(self, interaction_data):
        """Handle UI interaction events by converting them to Nova Sonic events"""
        if not self.nova_client:
            logger.error("No Nova Sonic client available for handling UI interaction")
            return

        if interaction_data.get("type") == "button_click":
            # Generate unique IDs for this interaction
            prompt_name = self.nova_client.prompt_name  # Use the existing prompt name
            content_name = f"button_click_{str(uuid.uuid4())}"
            
            # Send sequence of events to Nova Sonic
            events = [
                {
                    "event": {
                        "contentStart": {
                            "promptName": prompt_name,
                            "contentName": content_name,
                            "type": "TEXT",
                            "interactive": True,
                            "role": "USER",
                            "textInputConfiguration": {
                                "mediaType": "text/plain"
                            }
                        }
                    }
                },
                {
                    "event": {
                        "textInput": {
                            "promptName": prompt_name,
                            "contentName": content_name,
                            "content": "The user clicked a button. Please acknowledge this action and respond both in text and speech."
                        }
                    }
                },
                {
                    "event": {
                        "contentEnd": {
                            "promptName": prompt_name,
                            "contentName": content_name
                        }
                    }
                }
            ]
            
            # Send events to Nova Sonic
            for event in events:
                try:
                    await self.nova_client.send_event(json.dumps(event))
                    logger.info(f"Sent UI interaction event to Nova Sonic: {event}")
                except Exception as e:
                    logger.error(f"Error sending event to Nova Sonic: {e}")
                    logger.exception(e)

# Default (does not save audio files)
SAVE_DEBUG_AUDIO = os.getenv('SAVE_DEBUG_AUDIO', 'false').lower() == 'true'
manager = ConnectionManager(save_debug_audio=SAVE_DEBUG_AUDIO)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Get model and language from query parameters
    model_id = websocket.query_params.get("model", "amazon.nova-sonic-v1:0")
    language = websocket.query_params.get("language", "en")
    logger.info(f"New WebSocket connection request with model: {model_id}, language: {language}")
    await manager.connect(websocket, model_id=model_id, language=language)
    
    # Send tool configurations
    tool_configs = manager.nova_client.tool_manager.get_tool_configs() if manager.nova_client else []
    await websocket.send_text(json.dumps({
        "event": {
            "init": {
                "toolConfigs": tool_configs
            }
        }
    }))
    
    # Start processing audio responses and events in background
    process_task = asyncio.create_task(manager.process_audio_responses())
    event_task = asyncio.create_task(manager.process_events())
    
    try:
        while True:
            message = await websocket.receive()
            
            if "bytes" in message:
                # Handle audio data
                audio_data = message["bytes"]
                logger.debug(f"Received audio data of size {len(audio_data)} bytes")
                await manager.receive_audio(audio_data)
            elif "text" in message:
                # Parse the message to check for different event types
                try:
                    event_data = json.loads(message["text"])
                    logger.info(f"Received text message: {event_data}")
                    
                    if "event" in event_data:
                        event = event_data["event"]
                        if "ui_interaction" in event:
                            logger.info(f"Handling UI interaction: {event['ui_interaction']}")
                            await manager.handle_ui_interaction(event["ui_interaction"])
                        elif "toolUse" in event:
                            logger.info(f"Handling tool use: {event['toolUse']}")
                            await manager.handle_tool_use(event_data)
                        elif "textInput" in event:
                            # Add user message to history
                            user_text = event["textInput"].get("content", "")
                            manager.add_history("USER", user_text)
                        else:
                            # Handle string commands
                            command = message["text"]
                            if command == "start_audio":
                                await manager.start_audio()
                            elif command == "stop_audio":
                                await manager.stop_audio()
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message: {e}")
                    # Handle as regular command if not JSON
                    command = message["text"]
                    if command == "start_audio":
                        await manager.start_audio()
                    elif command == "stop_audio":
                        await manager.stop_audio()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        logger.exception(e)  # This will print the full stack trace
    finally:
        logger.info("Cleaning up WebSocket connection")
        process_task.cancel()
        event_task.cancel()
        await manager.disconnect()

for r in app_routers:
    app.include_router(r)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 