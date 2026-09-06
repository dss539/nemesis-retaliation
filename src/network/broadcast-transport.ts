import { NetworkTransport } from './coordinator.js';
import { NetworkMessage } from './types.js';

/**
 * High-performance browser transport using BroadcastChannel.
 * Enables zero-latency P2P action synchronization between multiple browser tabs/windows
 * or Playwright multi-browser test instances without requiring external signaling servers.
 */
export class BroadcastChannelTransport implements NetworkTransport {
  private channel: BroadcastChannel;
  public onMessage?: (msg: NetworkMessage) => void;

  constructor(channelName: string) {
    this.channel = new BroadcastChannel(channelName);
    this.channel.onmessage = (event: MessageEvent<NetworkMessage>) => {
      this.onMessage?.(event.data);
    };
  }

  public send(_targetPeerId: string, message: NetworkMessage): void {
    this.channel.postMessage(message);
  }

  public broadcast(message: NetworkMessage): void {
    this.channel.postMessage(message);
  }

  public close(): void {
    this.channel.close();
  }
}
