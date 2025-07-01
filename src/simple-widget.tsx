import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ILauncher } from '@jupyterlab/launcher';
import { ICommandPalette } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';

/**
 * Simple AI Chat Widget without React for now
 */
export class SimpleAIChatWidget extends Widget {
  constructor() {
    super();
    try {
      this.addClass('ai-chat-widget');
      this.title.label = 'AI Chat';
      this.title.closable = true;
      this.title.iconClass = 'jp-Icon jp-Icon-16';
      
      // Ensure the widget has a unique ID
      this.id = `ai-chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      
      this.createUI();
    } catch (error) {
      console.error('Error initializing SimpleAIChatWidget:', error);
    }
  }

  private createUI(): void {
    // Create main container
    const container = document.createElement('div');
    container.className = 'ai-chat-container';
    
    // Header
    const header = document.createElement('div');
    header.className = 'ai-chat-header';
    header.innerHTML = `
      <h3>🧠 AI Chat</h3>
      <div class="ai-chat-controls">
        <select class="model-selector" id="model-select">
          <option value="">Loading models...</option>
        </select>
        <label class="deep-research-toggle">
          <input type="checkbox" id="research-toggle"> 🔎 Deep Research
        </label>
      </div>
    `;
    
    // Parameters
    const params = document.createElement('div');
    params.className = 'ai-chat-parameters';
    params.innerHTML = `
      <div class="parameter-group">
        <label>Temperature: <span id="temp-value">0.7</span></label>
        <input type="range" id="temperature" min="0" max="2" step="0.1" value="0.7">
      </div>
      <div class="parameter-group">
        <label>Top P: <span id="topp-value">0.9</span></label>
        <input type="range" id="top_p" min="0" max="1" step="0.1" value="0.9">
      </div>
      <div class="parameter-group">
        <label>Max Tokens: <span id="tokens-value">512</span></label>
        <input type="range" id="max_tokens" min="1" max="2048" step="1" value="512">
      </div>
    `;
    
    // Messages area
    const messages = document.createElement('div');
    messages.className = 'ai-chat-messages';
    messages.id = 'messages-area';
    
    // Input area
    const inputArea = document.createElement('div');
    inputArea.className = 'ai-chat-input-area';
    inputArea.innerHTML = `
      <div class="input-controls">
        <input type="file" id="file-upload" style="display: none;" multiple accept=".txt,.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif">
        <label for="file-upload" class="file-upload-btn">📁</label>
        <textarea id="message-input" class="message-input" placeholder="Type your message here..."></textarea>
        <button id="send-button" class="send-button">🚀</button>
      </div>
    `;
    
    // Assemble UI
    container.appendChild(header);
    container.appendChild(params);
    container.appendChild(messages);
    container.appendChild(inputArea);
    
    this.node.appendChild(container);
    
    // Setup event handlers
    this.setupEventHandlers();
    
    // Load models
    this.loadModels();
  }

  private setupEventHandlers(): void {
    // Temperature slider
    const tempSlider = this.node.querySelector('#temperature') as HTMLInputElement;
    const tempValue = this.node.querySelector('#temp-value') as HTMLSpanElement;
    tempSlider?.addEventListener('input', () => {
      tempValue.textContent = tempSlider.value;
    });

    // Top P slider
    const toppSlider = this.node.querySelector('#top_p') as HTMLInputElement;
    const toppValue = this.node.querySelector('#topp-value') as HTMLSpanElement;
    toppSlider?.addEventListener('input', () => {
      toppValue.textContent = toppSlider.value;
    });

    // Max tokens slider
    const tokensSlider = this.node.querySelector('#max_tokens') as HTMLInputElement;
    const tokensValue = this.node.querySelector('#tokens-value') as HTMLSpanElement;
    tokensSlider?.addEventListener('input', () => {
      tokensValue.textContent = tokensSlider.value;
    });

    // Send button
    const sendButton = this.node.querySelector('#send-button') as HTMLButtonElement;
    sendButton?.addEventListener('click', () => this.sendMessage());

    // Enter key in textarea
    const messageInput = this.node.querySelector('#message-input') as HTMLTextAreaElement;
    messageInput?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
  }

  private async loadModels(): Promise<void> {
    try {
      const response = await fetch('/aichat/models');
      const models = await response.json();
      
      const select = this.node.querySelector('#model-select') as HTMLSelectElement;
      select.innerHTML = '<option value="">Select Model</option>';
      
      models.forEach((model: string) => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        select.appendChild(option);
      });
      
      if (models.length > 0) {
        select.value = models[0];
      }
    } catch (error) {
      console.error('Failed to load models:', error);
      const select = this.node.querySelector('#model-select') as HTMLSelectElement;
      select.innerHTML = '<option value="">Error loading models</option>';
    }
  }

  private async sendMessage(): Promise<void> {
    const messageInput = this.node.querySelector('#message-input') as HTMLTextAreaElement;
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Get form values
    const modelSelect = this.node.querySelector('#model-select') as HTMLSelectElement;
    const tempSlider = this.node.querySelector('#temperature') as HTMLInputElement;
    const toppSlider = this.node.querySelector('#top_p') as HTMLInputElement;
    const tokensSlider = this.node.querySelector('#max_tokens') as HTMLInputElement;
    const researchToggle = this.node.querySelector('#research-toggle') as HTMLInputElement;
    
    // Add user message to UI
    this.addMessage('user', message);
    messageInput.value = '';
    
    // Show loading
    this.addMessage('assistant', 'Thinking...', true);
    
    try {
      const formData = new FormData();
      formData.append('message', message);
      formData.append('model', modelSelect.value);
      formData.append('temperature', tempSlider.value);
      formData.append('top_p', toppSlider.value);
      formData.append('max_tokens', tokensSlider.value);
      formData.append('deep_research', researchToggle.checked.toString());
      
      const response = await fetch('/aichat/chat', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      // Remove loading message and add real response
      this.removeLastMessage();
      this.addMessage('assistant', result.response || 'No response received');
      
    } catch (error) {
      this.removeLastMessage();
      this.addMessage('assistant', 'Sorry, I encountered an error processing your request.');
      console.error('Chat error:', error);
    }
  }

  private addMessage(role: 'user' | 'assistant', content: string, isLoading: boolean = false): void {
    const messagesArea = this.node.querySelector('#messages-area') as HTMLDivElement;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    if (isLoading) messageDiv.classList.add('loading');
    
    const time = new Date().toLocaleTimeString();
    const icon = role === 'user' ? '👤 You' : '🤖 Assistant';
    
    messageDiv.innerHTML = `
      <div class="message-header">
        <strong>${icon}</strong>
        <span class="timestamp">${time}</span>
      </div>
      <div class="message-content">${content}</div>
    `;
    
    messagesArea.appendChild(messageDiv);
    messagesArea.scrollTop = messagesArea.scrollHeight;
  }

  private removeLastMessage(): void {
    const messagesArea = this.node.querySelector('#messages-area') as HTMLDivElement;
    const lastMessage = messagesArea.lastElementChild;
    if (lastMessage) {
      messagesArea.removeChild(lastMessage);
    }
  }
}

/**
 * Initialization data for the jupyterlab-ai-chat extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-ai-chat:plugin',
  autoStart: true,
  requires: [ILauncher],
  optional: [ICommandPalette],
  activate: (
    app: JupyterFrontEnd,
    launcher: ILauncher,
    palette: ICommandPalette | null
  ) => {
    console.log('JupyterLab extension jupyterlab-ai-chat is activated!');

    // Ensure launcher is properly initialized
    if (!launcher) {
      console.error('Launcher not available');
      return;
    }

    const command = 'aichat:open';
    
    try {
      app.commands.addCommand(command, {
        label: 'AI Chat',
        caption: 'Open a new AI Chat session',
        icon: 'jp-Icon jp-Icon-16',
        execute: () => {
          try {
            const widget = new SimpleAIChatWidget();
            app.shell.add(widget, 'main');
            // Activate the widget after ensuring it has been added
            if (widget.id) {
              app.shell.activateById(widget.id);
            }
          } catch (error) {
            console.error('Error creating AI Chat widget:', error);
          }
        }
      });
    } catch (error) {
      console.error('Error adding command:', error);
      return;
    }

    // Add to launcher with explicit ID
    try {
      launcher.add({
        command,
        category: 'Other',
        rank: 1
      });
    } catch (error) {
      console.error('Error adding to launcher:', error);
    }

    // Add to command palette
    try {
      if (palette) {
        palette.addItem({
          command,
          category: 'AI Tools'
        });
      }
    } catch (error) {
      console.error('Error adding to command palette:', error);
    }
  }
};

export default plugin; 