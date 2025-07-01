import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ILauncher } from '@jupyterlab/launcher';
import { Widget } from '@lumino/widgets';

/**
 * Simple working widget for JupyterLab 3.6.8
 */
class WorkingWidget extends Widget {
  constructor() {
    super();
    this.id = `working-widget-${Date.now()}`;
    this.title.label = 'AI Chat';
    this.title.closable = true;
    
    // Simple HTML content
    this.node.innerHTML = `
      <div style="padding: 20px; font-family: sans-serif;">
        <h2>🧠 AI Chat Extension</h2>
        <p>Extension loaded successfully!</p>
        <div style="margin-top: 20px;">
          <textarea placeholder="Type your message..." style="width: 100%; height: 100px; margin-bottom: 10px;"></textarea>
          <button onclick="alert('Chat functionality would work here!')">Send Message</button>
        </div>
      </div>
    `;
  }
}

/**
 * Simple plugin compatible with JupyterLab 3.6.8
 */
const simplePlugin: JupyterFrontEndPlugin<void> = {
  id: 'working-ai-chat',
  autoStart: true,
  requires: [ILauncher],
  activate: (app: JupyterFrontEnd, launcher: ILauncher) => {
    console.log('Working AI Chat extension activated');
    
    app.commands.addCommand('working-ai-chat:open', {
      label: 'AI Chat',
      execute: () => {
        const widget = new WorkingWidget();
        app.shell.add(widget, 'main');
        app.shell.activateById(widget.id);
      }
    });

    launcher.add({
      command: 'working-ai-chat:open',
      category: 'Other'
    });
  }
};

export default simplePlugin; 