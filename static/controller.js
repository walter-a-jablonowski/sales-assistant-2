let currentConversationId = null;

document.addEventListener('DOMContentLoaded', () =>
{
  loadConversations();
  
  document.getElementById('chat-form').addEventListener('submit', handleSubmit);
  document.getElementById('new-chat-btn').addEventListener('click', startNewChat);
  
  const userInput = document.getElementById('user-input');
  userInput.addEventListener('keydown', (e) =>
  {
    if( e.key === 'Enter' && !e.shiftKey )
    {
      e.preventDefault();
      document.getElementById('chat-form').dispatchEvent(new Event('submit'));
    }
  });
  
  setupMobileMenu();
  attachSampleQuestionListeners();
});

function setupMobileMenu()
{
  const menuToggle = document.getElementById('menu-toggle');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  
  menuToggle.addEventListener('click', () =>
  {
    sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
  });
  
  overlay.addEventListener('click', () =>
  {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
  });
}

function closeMobileMenu()
{
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  
  if( sidebar.classList.contains('open') )
  {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
  }
}

function attachSampleQuestionListeners()
{
  document.querySelectorAll('.welcome-message li').forEach(li =>
  {
    li.addEventListener('click', () =>
    {
      const question = li.textContent;
      document.getElementById('user-input').value = question;
      document.getElementById('chat-form').dispatchEvent(new Event('submit'));
    });
  });
}

async function loadConversations()
{
  try
  {
    const response = await fetch('/api/conversations');
    const data = await response.json();
    
    const conversationList = document.getElementById('conversation-list');
    conversationList.innerHTML = '';
    
    if( data.conversations && data.conversations.length > 0 )
    {
      data.conversations.forEach(conv =>
      {
        const convElement = createConversationElement(conv);
        conversationList.appendChild(convElement);
      });
    }
    else
    {
      conversationList.innerHTML = '<p class="no-conversations">No conversations yet</p>';
    }
  }
  catch( error )
  {
    console.error('Error loading conversations:', error);
  }
}

function createConversationElement(conversation)
{
  const div = document.createElement('div');
  div.className = 'conversation-item';
  if( conversation.id === currentConversationId )
    div.classList.add('active');
  
  div.innerHTML = `
    <div class="conversation-content">
      <div class="conversation-title">${escapeHtml(conversation.title)}</div>
      <div class="conversation-meta">${formatDate(conversation.created_at)} · ${conversation.message_count} messages</div>
    </div>
    <button class="btn-delete" data-id="${conversation.id}">×</button>
  `;
  
  div.querySelector('.conversation-content').addEventListener('click', () =>
  {
    loadConversation(conversation.id);
  });
  
  div.querySelector('.btn-delete').addEventListener('click', (e) =>
  {
    e.stopPropagation();
    deleteConversation(conversation.id);
  });
  
  return div;
}

async function loadConversation(conversationId)
{
  try
  {
    closeMobileMenu();
    
    const response = await fetch(`/api/conversations/${conversationId}`);
    const conversation = await response.json();
    
    currentConversationId = conversationId;
    
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = '';
    
    conversation.messages.forEach((msg, index) =>
    {
      if( msg.role === 'user' )
      {
        addUserMessage(msg.content, index);
      }
      else if( msg.role === 'assistant' )
      {
        addAssistantMessage(msg.content, msg.function_results || []);
      }
      else if( msg.role === 'error' )
      {
        addErrorMessage(msg.content, msg.is_critical || false);
      }
    });
    
    document.querySelectorAll('.conversation-item').forEach(item =>
    {
      item.classList.remove('active');
    });
    
    const activeItem = document.querySelector(`[data-id="${conversationId}"]`)?.closest('.conversation-item');
    if( activeItem )
      activeItem.classList.add('active');
    
    scrollToBottom();
  }
  catch( error )
  {
    console.error('Error loading conversation:', error);
    showError('Failed to load conversation');
  }
}

async function deleteConversation(conversationId)
{
  if( !await showDeleteDialog() )
    return;
  
  try
  {
    const response = await fetch(`/api/conversations/${conversationId}`, {
      method: 'DELETE'
    });
    
    if( response.ok )
    {
      if( currentConversationId === conversationId )
      {
        currentConversationId = null;
        document.getElementById('chat-messages').innerHTML = `
          <div class="welcome-message">
            <h2>Welcome to Sales Assistant</h2>
            <p>Ask me anything about your sales data. For example:</p>
            <ul>
              <li>What are the top 5 customers by order value?</li>
              <li>Show me all products in the Electronics category</li>
              <li>What were the sales sum last month?</li>
              <li>Which products have low stock?</li>
            </ul>
          </div>
        `;
        attachSampleQuestionListeners();
      }
      
      loadConversations();
    }
  }
  catch( error )
  {
    console.error('Error deleting conversation:', error);
    showError('Failed to delete conversation');
  }
}

function startNewChat()
{
  closeMobileMenu();
  
  currentConversationId = null;
  
  const chatMessages = document.getElementById('chat-messages');
  chatMessages.innerHTML = `
    <div class="welcome-message">
      <h2>Welcome to Sales Assistant</h2>
      <p>Ask me anything about your sales data. For example:</p>
      <ul>
        <li>What are the top 5 customers by order value?</li>
        <li>Show me all products in the Electronics category</li>
        <li>What were the sales sum last month?</li>
        <li>Which products have low stock?</li>
      </ul>
    </div>
  `;
  
  attachSampleQuestionListeners();
  
  document.querySelectorAll('.conversation-item').forEach(item =>
  {
    item.classList.remove('active');
  });
  
  document.getElementById('user-input').focus();
}

async function handleSubmit(e)
{
  e.preventDefault();
  
  const input = document.getElementById('user-input');
  const message = input.value.trim();
  
  if( !message )
    return;
  
  input.value = '';
  input.disabled = true;
  document.getElementById('send-btn').disabled = true;
  
  addUserMessage(message);
  
  const loadingDiv = addLoadingMessage();
  
  try
  {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: message,
        conversation_id: currentConversationId
      })
    });
    
    const data = await response.json();
    
    loadingDiv.remove();
    
    if( response.ok )
    {
      if( !currentConversationId )
      {
        currentConversationId = data.conversation_id;
        loadConversations();
      }
      
      addAssistantMessage(data.message, data.function_results || []);
    }
    else
    {
      const isCritical = data.is_critical !== false;
      
      if( isCritical )
      {
        showCriticalError(data.error || 'A critical error occurred');
        return;
      }
      
      if( data.conversation_id )
      {
        currentConversationId = data.conversation_id;
        loadConversations();
      }
      
      addErrorMessage(data.error || 'An error occurred', false);
    }
  }
  catch( error )
  {
    loadingDiv.remove();
    console.error('Error:', error);
    showCriticalError('Failed to send message. Please check your connection and try again.');
  }
  finally
  {
    input.disabled = false;
    document.getElementById('send-btn').disabled = false;
    input.focus();
  }
}

function addUserMessage(content, messageIndex = null)
{
  const chatMessages = document.getElementById('chat-messages');
  
  const welcomeMsg = chatMessages.querySelector('.welcome-message');
  if( welcomeMsg )
    welcomeMsg.remove();
  
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message user-message';
  if( messageIndex !== null )
  {
    messageDiv.dataset.messageIndex = messageIndex;
  }
  
  messageDiv.innerHTML = `
    <div class="message-content">
      <div class="message-text">${escapeHtml(content)}</div>
      <button class="edit-message-btn" onclick="editUserMessage(${messageIndex})" title="Edit and re-run">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
      </button>
    </div>
  `;
  
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

function addAssistantMessage(content, functionResults)
{
  const chatMessages = document.getElementById('chat-messages');
  
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message assistant-message';
  
  let html = '<div class="message-content">';
  
  if( functionResults && functionResults.length > 0 )
  {
    functionResults.forEach(result =>
    {
      if( result.type === 'table' )
      {
        html += renderTable(result);
      }
      else if( result.type === 'diagram' )
      {
        html += renderDiagram(result);
      }
      else if( result.type === 'error' )
      {
        html += renderError(result);
      }
    });
  }
  
  if( content )
  {
    html += `<div class="message-text">${markdownToHtml(content)}</div>`;
  }
  
  html += '</div>';
  
  messageDiv.innerHTML = html;
  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

function renderTable(result)
{
  let html = '<div class="result-table">';
  
  if( result.query )
  {
    const queryId = 'query-' + Math.random().toString(36).substr(2, 9);
    html += `<div class="sql-query-collapsible">
      <button class="sql-query-toggle" onclick="toggleSqlQuery('${queryId}')">
        <span class="toggle-icon">▶</span>
        <span class="toggle-label">SQL Query</span>
      </button>
      <div class="sql-query-content" id="${queryId}">
        <code>${escapeHtml(result.query)}</code>
      </div>
    </div>`;
  }
  
  if( result.table_name )
  {
    html += `<div class="table-title">Sample data from <strong>${result.table_name}</strong></div>`;
  }
  
  html += '<div class="table-wrapper"><table>';
  
  html += '<thead><tr>';
  result.columns.forEach(col =>
  {
    html += `<th>${escapeHtml(col)}</th>`;
  });
  html += '</tr></thead>';
  
  html += '<tbody>';
  result.rows.forEach(row =>
  {
    html += '<tr>';
    row.forEach(cell =>
    {
      html += `<td>${escapeHtml(cell)}</td>`;
    });
    html += '</tr>';
  });
  html += '</tbody>';
  
  html += '</table></div>';
  
  html += `<div class="table-footer">${result.row_count} row${result.row_count !== 1 ? 's' : ''}</div>`;
  
  html += '</div>';
  
  return html;
}

function renderDiagram(result)
{
  const chartId = 'chart-' + Math.random().toString(36).substr(2, 9);
  
  let html = '<div class="result-diagram">';
  
  if( result.title )
  {
    html += `<div class="diagram-title">${escapeHtml(result.title)}</div>`;
  }
  
  html += `<div class="chart-container">
    <canvas id="${chartId}"></canvas>
  </div>`;
  
  html += '</div>';
  
  setTimeout(() =>
  {
    createChart(chartId, result);
  }, 100);
  
  return html;
}

function createChart(chartId, result)
{
  const canvas = document.getElementById(chartId);
  if( !canvas )
    return;
  
  const ctx = canvas.getContext('2d');
  
  const colorPalette = [
    'rgba(59, 130, 246, 0.8)',
    'rgba(16, 185, 129, 0.8)',
    'rgba(249, 115, 22, 0.8)',
    'rgba(139, 92, 246, 0.8)',
    'rgba(236, 72, 153, 0.8)',
    'rgba(245, 158, 11, 0.8)',
    'rgba(20, 184, 166, 0.8)',
    'rgba(239, 68, 68, 0.8)',
    'rgba(168, 85, 247, 0.8)',
    'rgba(34, 197, 94, 0.8)'
  ];
  
  const borderColorPalette = [
    'rgba(59, 130, 246, 1)',
    'rgba(16, 185, 129, 1)',
    'rgba(249, 115, 22, 1)',
    'rgba(139, 92, 246, 1)',
    'rgba(236, 72, 153, 1)',
    'rgba(245, 158, 11, 1)',
    'rgba(20, 184, 166, 1)',
    'rgba(239, 68, 68, 1)',
    'rgba(168, 85, 247, 1)',
    'rgba(34, 197, 94, 1)'
  ];
  
  const datasets = result.datasets.map((dataset, index) =>
  {
    const isPieType = ['pie', 'doughnut', 'polarArea'].includes(result.chart_type);
    
    return {
      label: dataset.label,
      data: dataset.data,
      backgroundColor: isPieType ? colorPalette : colorPalette[index % colorPalette.length],
      borderColor: isPieType ? borderColorPalette : borderColorPalette[index % borderColorPalette.length],
      borderWidth: 2,
      tension: result.chart_type === 'line' ? 0.4 : 0
    };
  });
  
  new Chart(ctx, {
    type: result.chart_type,
    data: {
      labels: result.labels,
      datasets: datasets
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          enabled: true,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          titleFont: { size: 14 },
          bodyFont: { size: 13 }
        }
      },
      scales: ['pie', 'doughnut', 'polarArea', 'radar'].includes(result.chart_type) ? {} : {
        y: {
          beginAtZero: true,
          ticks: {
            font: { size: 11 }
          }
        },
        x: {
          ticks: {
            font: { size: 11 }
          }
        }
      }
    }
  });
}

function renderError(result)
{
  let html = '<div class="error-message">';
  html += `<strong>Error:</strong> ${escapeHtml(result.error)}`;
  
  if( result.query )
  {
    const queryId = 'query-' + Math.random().toString(36).substr(2, 9);
    html += `<div class="sql-query-collapsible">
      <button class="sql-query-toggle" onclick="toggleSqlQuery('${queryId}')">
        <span class="toggle-icon">▶</span>
        <span class="toggle-label">Query</span>
      </button>
      <div class="sql-query-content" id="${queryId}">
        <code>${escapeHtml(result.query)}</code>
      </div>
    </div>`;
  }
  
  html += '</div>';
  
  return html;
}

function addLoadingMessage()
{
  const chatMessages = document.getElementById('chat-messages');
  
  const loadingDiv = document.createElement('div');
  loadingDiv.className = 'message assistant-message loading';
  loadingDiv.innerHTML = `
    <div class="message-content">
      <div class="loading-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  `;
  
  chatMessages.appendChild(loadingDiv);
  scrollToBottom();
  
  return loadingDiv;
}

function addErrorMessage(message, isCritical)
{
  const chatMessages = document.getElementById('chat-messages');
  
  const errorDiv = document.createElement('div');
  errorDiv.className = 'message assistant-message';
  errorDiv.innerHTML = `
    <div class="message-content">
      <div class="error-message ${isCritical ? 'critical-error' : ''}">
        <strong>${isCritical ? 'Critical Error' : 'Error'}:</strong> ${escapeHtml(message)}
      </div>
    </div>
  `;
  
  chatMessages.appendChild(errorDiv);
  scrollToBottom();
}

function showCriticalError(message)
{
  document.body.innerHTML = `
    <div class="critical-error-page">
      <div class="critical-error-content">
        <div class="critical-error-icon">⚠</div>
        <h1>Critical Error</h1>
        <p class="critical-error-message">${escapeHtml(message)}</p>
        <p class="critical-error-help">The application encountered a critical error and can't continue. Please refresh the page to try again.</p>
        <button class="btn-reload" onclick="location.reload()">Reload Application</button>
      </div>
    </div>
  `;
}

function scrollToBottom()
{
  const chatMessages = document.getElementById('chat-messages');
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text)
{
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function markdownToHtml(text)
{
  if( !text )
    return '';
  
  let html = escapeHtml(text);
  
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  html = html.replace(/_(.+?)_/g, '<em>$1</em>');
  html = html.replace(/`(.+?)`/g, '<code>$1</code>');
  html = html.replace(/\n/g, '<br>');
  
  return html;
}

function formatDate(isoString)
{
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if( diffMins < 1 )
    return 'Just now';
  if( diffMins < 60 )
    return `${diffMins}m ago`;
  if( diffHours < 24 )
    return `${diffHours}h ago`;
  if( diffDays < 7 )
    return `${diffDays}d ago`;
  
  return date.toLocaleDateString();
}

function toggleSqlQuery(queryId)
{
  const content = document.getElementById(queryId);
  const button = content.previousElementSibling;
  const icon = button.querySelector('.toggle-icon');
  
  if( content.classList.contains('expanded') )
  {
    content.classList.remove('expanded');
    icon.textContent = '▶';
  }
  else
  {
    content.classList.add('expanded');
    icon.textContent = '▼';
  }
}

async function editUserMessage(messageIndex)
{
  if( !currentConversationId )
    return;
  
  try
  {
    const response = await fetch(`/api/conversations/${currentConversationId}`);
    const conversation = await response.json();
    
    if( !conversation.messages[messageIndex] || conversation.messages[messageIndex].role !== 'user' )
      return;
    
    const originalMessage = conversation.messages[messageIndex].content;
    
    const messageDiv = document.querySelector(`.user-message[data-message-index="${messageIndex}"]`);
    if( !messageDiv )
      return;
    
    const messageTextDiv = messageDiv.querySelector('.message-text');
    const editBtn = messageDiv.querySelector('.edit-message-btn');
    
    editBtn.style.display = 'none';
    
    const textarea = document.createElement('textarea');
    textarea.className = 'edit-message-textarea';
    textarea.value = originalMessage;
    textarea.rows = Math.min(10, originalMessage.split('\n').length + 1);
    
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'edit-message-actions';
    
    const saveBtn = document.createElement('button');
    saveBtn.className = 'edit-save-btn';
    saveBtn.textContent = 'Save & Re-run';
    
    const cancelBtn = document.createElement('button');
    cancelBtn.className = 'edit-cancel-btn';
    cancelBtn.textContent = 'Cancel';
    
    buttonContainer.appendChild(saveBtn);
    buttonContainer.appendChild(cancelBtn);
    
    messageTextDiv.style.display = 'none';
    messageDiv.querySelector('.message-content').appendChild(textarea);
    messageDiv.querySelector('.message-content').appendChild(buttonContainer);
    
    textarea.focus();
    textarea.select();
    
    const cleanup = () =>
    {
      textarea.remove();
      buttonContainer.remove();
      messageTextDiv.style.display = 'block';
      editBtn.style.display = 'block';
    };
    
    cancelBtn.onclick = cleanup;
    
    saveBtn.onclick = async () =>
    {
      const editedMessage = textarea.value.trim();
      if( !editedMessage )
        return;
      
      saveBtn.disabled = true;
      saveBtn.textContent = 'Processing...';
      
      try
      {
        const chatMessages = document.getElementById('chat-messages');
        const messagesToRemove = [];
        let foundTarget = false;
        
        chatMessages.querySelectorAll('.message').forEach(msg =>
        {
          if( msg === messageDiv )
          {
            foundTarget = true;
            return;
          }
          if( foundTarget )
          {
            messagesToRemove.push(msg);
          }
        });
        
        messagesToRemove.forEach(msg => msg.remove());
        
        cleanup();
        messageTextDiv.textContent = editedMessage;
        
        const loadingDiv = addLoadingMessage();
        
        const rerunResponse = await fetch('/api/chat/rerun', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            conversation_id: currentConversationId,
            message_index: messageIndex,
            new_message: editedMessage
          })
        });
        
        loadingDiv.remove();
        
        if( rerunResponse.ok )
        {
          const result = await rerunResponse.json();
          
          const updatedConv = await fetch(`/api/conversations/${currentConversationId}`);
          const updatedConversation = await updatedConv.json();
          
          for( let i = messageIndex + 1; i < updatedConversation.messages.length; i++ )
          {
            const msg = updatedConversation.messages[i];
            if( msg.role === 'assistant' )
            {
              addAssistantMessage(msg.content, msg.function_results || []);
            }
            else if( msg.role === 'error' )
            {
              addErrorMessage(msg.content, msg.is_critical || false);
            }
          }
        }
        else
        {
          addErrorMessage('Failed to re-run message', false);
        }
      }
      catch( error )
      {
        console.error('Error re-running message:', error);
        addErrorMessage('Failed to re-run message', false);
        cleanup();
      }
    };
  }
  catch( error )
  {
    console.error('Error editing message:', error);
    addErrorMessage('Failed to edit message', false);
  }
}

function showDeleteDialog()
{
  return new Promise((resolve) =>
  {
    const dialog = document.createElement('div');
    dialog.className = 'delete-dialog-overlay';
    dialog.innerHTML = `
      <div class="delete-dialog">
        <h3>Delete chat?</h3>
        <p>This will delete the conversation permanently.</p>
        <div class="delete-dialog-buttons">
          <button class="btn-cancel">Cancel</button>
          <button class="btn-confirm-delete">Delete</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(dialog);
    
    const handleDelete = () =>
    {
      dialog.remove();
      resolve(true);
    };
    
    const handleCancel = () =>
    {
      dialog.remove();
      resolve(false);
    };
    
    dialog.querySelector('.btn-confirm-delete').addEventListener('click', handleDelete);
    dialog.querySelector('.btn-cancel').addEventListener('click', handleCancel);
    dialog.addEventListener('click', (e) =>
    {
      if( e.target === dialog )
        handleCancel();
    });
    
    setTimeout(() => dialog.querySelector('.btn-cancel').focus(), 100);
  });
}
