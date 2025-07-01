import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ILauncher } from '@jupyterlab/launcher';
import { Widget } from '@lumino/widgets';

/**
 * Minimal test widget
 */
class MinimalWidget extends Widget {
  constructor() {
    super();
    this.id = `minimal-widget-${Date.now()}`;
    this.title.label = 'Test Widget';
    this.title.closable = true;
    
    const div = document.createElement('div');
    div.innerHTML = '<h1>Test Widget Working!</h1>';
    this.node.appendChild(div);
  }
}

/**
 * Minimal test plugin
 */
const minimalPlugin: JupyterFrontEndPlugin<void> = {
  id: 'minimal-test:plugin',
  autoStart: true,
  requires: [ILauncher],
  activate: (app: JupyterFrontEnd, launcher: ILauncher) => {
    console.log('Minimal test plugin activated');
    
    const command = 'minimal:test';
    
    app.commands.addCommand(command, {
      label: 'Test Minimal',
      execute: () => {
        const widget = new MinimalWidget();
        app.shell.add(widget, 'main');
        if (widget.id) {
          app.shell.activateById(widget.id);
        }
      }
    });

    launcher.add({
      command,
      category: 'Other'
    });
  }
};

export default minimalPlugin; 