// static/js/app.js
// Alpine.js components for agent-tui web interface

document.addEventListener('alpine:init', () => {
  Alpine.data('chatApp', () => ({
    message: '',
    isStreaming: false,
    showProjectModal: false,
    currentProject: null,
    
    init() {
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },
    
    scrollToBottom() {
      const container = this.$refs.messagesContainer;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },
    
    async sendMessage(chatId) {
      if (!this.message.trim() || this.isStreaming) return;
      
      this.isStreaming = true;
      const messageText = this.message;
      this.message = '';
      
      // Send via WebSocket
      if (window.ws && window.ws.readyState === WebSocket.OPEN) {
        window.ws.send(JSON.stringify({
          type: 'chat',
          message: messageText,
          thread_id: chatId
        }));
      } else {
        console.error('WebSocket not connected');
        this.isStreaming = false;
        alert('Not connected to server. Please refresh the page.');
      }
    },
    
    onStreamComplete() {
      this.isStreaming = false;
      this.$nextTick(() => this.scrollToBottom());
    }
  }));
  
  Alpine.data('approvalModal', () => ({
    show: false,
    toolName: '',
    toolArgs: {},
    toolId: '',
    
    open(toolName, toolArgs, toolId) {
      this.toolName = toolName;
      this.toolArgs = toolArgs;
      this.toolId = toolId;
      this.show = true;
    },
    
    close() {
      this.show = false;
    },
    
    approve() {
      this.$dispatch('tool-approved', { toolId: this.toolId, approved: true });
      this.close();
    },
    
    reject() {
      this.$dispatch('tool-approved', { toolId: this.toolId, approved: false });
      this.close();
    }
  }));
});
