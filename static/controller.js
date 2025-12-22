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
    
    conversation.messages.forEach(msg =>
    {
      if( msg.role === 'user' )
      {
        addUserMessage(msg.content);
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

function addUserMessage(content)
{
  const chatMessages = document.getElementById('chat-messages');
  
  const welcomeMsg = chatMessages.querySelector('.welcome-message');
  if( welcomeMsg )
    welcomeMsg.remove();
  
  const messageDiv = document.createElement('div');
  messageDiv.className = 'message user-message';
  messageDiv.innerHTML = `
    <div class="message-content">
      <div class="message-text">${escapeHtml(content)}</div>
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
      else if( result.type === 'error' )
      {
        html += renderError(result);
      }
    });
  }
  
  if( content )
  {
    html += `<div class="message-text">${escapeHtml(content)}</div>`;
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
    html += `<div class="sql-query">
      <strong>SQL Query:</strong>
      <code>${escapeHtml(result.query)}</code>
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

function renderError(result)
{
  let html = '<div class="error-message">';
  html += `<strong>Error:</strong> ${escapeHtml(result.error)}`;
  
  if( result.query )
  {
    html += `<div class="sql-query">
      <strong>Query:</strong>
      <code>${escapeHtml(result.query)}</code>
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
