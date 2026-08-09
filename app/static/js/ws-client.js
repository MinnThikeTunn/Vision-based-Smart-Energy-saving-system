/**
 * Robust WebSocket Telemetry Client with Exponential Backoff & Jitter
 */
export class RobustWebSocket {
  constructor(url, onMessage, onStatusChange) {
    this.url = url;
    this.onMessage = onMessage;
    this.onStatusChange = onStatusChange;
    this.ws = null;
    this.retryCount = 0;
    this.maxRetries = 10;
    this.baseDelay = 1000;
  }

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    if (this.onStatusChange) this.onStatusChange('CONNECTING');
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      this.retryCount = 0;
      if (this.onStatusChange) this.onStatusChange('CONNECTED');
    };

    this.ws.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data);
        if (this.onMessage) this.onMessage(data);
      } catch (err) {
        console.error('Failed to parse telemetry JSON:', err);
      }
    };

    this.ws.onerror = (err) => {
      console.error('WebSocket Error:', err);
    };

    this.ws.onclose = () => {
      if (this.onStatusChange) this.onStatusChange('DISCONNECTED');
      if (this.retryCount < this.maxRetries) {
        const delay = Math.min(30000, this.baseDelay * Math.pow(2, this.retryCount)) + (Math.random() * 500);
        this.retryCount++;
        setTimeout(() => this.connect(), delay);
      }
    };
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }
}
