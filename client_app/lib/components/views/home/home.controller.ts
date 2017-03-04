import * as ng from 'angular';

class HomeController implements ng.IComponentController{
	public socket : WebSocket;
	public socketActive : boolean;

	constructor(){
		// URL for the websocket connection
		const socketUrl = 'ws://0.0.0.0:8080';
		this.socketActive = false;
		
		// Init websocket
		this.socket = new WebSocket(socketUrl);
		this.socket.addEventListener('open', () => this.socketActive = true);

		// Add respective events to the websockets
		this.addEvents(this.socket);
	}

	addEvents(socket : WebSocket){
		/* Add respective events to the websockets */
		//socket.addEventListener('message', this.wsMessage);
	}

	convertFloat32ToInt16(buffer){
		/* Convert the float32 to a 16bit int */

		// TBH I copied this from a tutorial
		const l = buffer.length;
	  const buf = new Int16Array(l);
	  while (l--) {
	    buf[l] = Math.min(1, buffer[l])*0x7FFF;
	  }

	  return buf.buffer;
	} 

	startAudioStream(){
		/* Function to initialize streaming audio from the client to the server */

		// Socket must be open
		if (!this.socketActive){
			return;
		}

		// Create the stream
		window.navigator.getUserMedia({audio: true, video: false}, (stream) => {

			// Set up audio context object
			const context = new AudioContext();
			const audioInput = context.createMediaStreamSource(stream);

			// Create script processor which will send data to the websocket
			const bufferSize = 2048;
			const recorder = context.createScriptProcessor(bufferSize, 1, 1);

			recorder.onaudioprocess = (event) => {
				// Only getting the left channel data, may want to change
				const left = event.inputBuffer.getChannelData(0);

				// Convert the int16 and send
				this.socket.send(this.convertFloat32ToInt16(left));
			}

			audioInput.connect(recorder);
			recorder.connect(context.destination);

		}, (error) => console.error(error));
	}
}

HomeController.$inject = [];

export default HomeController;