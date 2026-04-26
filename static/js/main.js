// ──────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────
const csrfToken = () => document.querySelector('[name=csrfmiddlewaretoken]')?.value;

function getAvatar(username, avatar, size = 36) {
  if (avatar) {
    return `<img src="${avatar}" class="avatar" width="${size}" height="${size}" alt="${username}">`;
  }
  return `<div class="avatar-fallback" style="width:${size}px;height:${size}px;font-size:${size / 2.6}px">${username[0].toUpperCase()}</div>`;
}

function timesince(dateStr) {
  return dateStr || 'Just now';
}

// Auto-dismiss toasts
document.querySelectorAll('.toast').forEach(t => {
  setTimeout(() => t.remove(), 4500);
});

// ──────────────────────────────────────────────
// Navbar Dropdowns
// ──────────────────────────────────────────────
function setupDropdown(triggerId, menuId, toggleOnClick = true) {
  const trigger = document.getElementById(triggerId);
  const menu = document.getElementById(menuId);
  if (!trigger || !menu) return;

  trigger.addEventListener('click', (e) => {
    e.stopPropagation();
    const isOpen = menu.classList.contains('open');
    document.querySelectorAll('.dropdown-menu.open, .notif-dropdown.open').forEach(m => m.classList.remove('open'));
    if (!isOpen) menu.classList.add('open');
  });

  document.addEventListener('click', () => menu.classList.remove('open'));
  menu.addEventListener('click', e => e.stopPropagation());
}

setupDropdown('userMenuTrigger', 'userDropdown');

// ──────────────────────────────────────────────
// Custom Select / Dropdown Override
// ──────────────────────────────────────────────
function initCustomSelects() {
  document.querySelectorAll('select.privacy-select, select.form-control').forEach(select => {
    if (select.dataset.customized) return;
    select.dataset.customized = 'true';
    select.style.display = 'none';

    const wrapper = document.createElement('div');
    wrapper.className = 'custom-select-wrapper ' + (select.classList.contains('privacy-select') ? 'inline' : '');
    
    const selectedOpt = select.options[select.selectedIndex];
    
    const trigger = document.createElement('div');
    // keep base class styling but remove select-specific bg
    trigger.className = 'custom-select-trigger ' + select.className.replace('privacy-select', '').replace('form-control', '');
    trigger.innerHTML = `<span class="c-val">${selectedOpt ? selectedOpt.textContent : ''}</span> <i class="fa-solid fa-chevron-down" style="font-size:.7rem;opacity:.7"></i>`;
    
    const optionsContainer = document.createElement('div');
    optionsContainer.className = 'custom-select-options';
    
    Array.from(select.options).forEach(opt => {
      const optionDiv = document.createElement('div');
      optionDiv.className = 'custom-option' + (opt.selected ? ' selected' : '');
      optionDiv.innerHTML = opt.innerHTML; // preserves emojis/icons
      optionDiv.dataset.value = opt.value;
      
      optionDiv.addEventListener('click', () => {
        select.value = opt.value;
        trigger.querySelector('.c-val').innerHTML = opt.innerHTML;
        optionsContainer.querySelectorAll('.custom-option').forEach(o => o.classList.remove('selected'));
        optionDiv.classList.add('selected');
        wrapper.classList.remove('open');
        select.dispatchEvent(new Event('change'));
      });
      optionsContainer.appendChild(optionDiv);
    });
    
    wrapper.appendChild(trigger);
    wrapper.appendChild(optionsContainer);
    select.parentNode.insertBefore(wrapper, select.nextSibling);
    
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      document.querySelectorAll('.custom-select-wrapper.open').forEach(w => {
        if(w !== wrapper) w.classList.remove('open');
      });
      wrapper.classList.toggle('open');
    });
  });
  
  if (!window.customSelectListenerAttached) {
    document.addEventListener('click', () => {
      document.querySelectorAll('.custom-select-wrapper.open').forEach(w => w.classList.remove('open'));
    });
    window.customSelectListenerAttached = true;
  }
}
document.addEventListener('DOMContentLoaded', initCustomSelects);
// Run once immediately in case scripts load later
initCustomSelects();

// Notification bell
const bellLink = document.getElementById('notif-bell-link');
const notifDD = document.getElementById('notifDropdown');
if (bellLink && notifDD) {
  bellLink.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    const isOpen = notifDD.classList.contains('open');
    document.querySelectorAll('.dropdown-menu.open').forEach(m => m.classList.remove('open'));
    if (!isOpen) {
      notifDD.classList.add('open');
      loadNotifications();
    } else {
      notifDD.classList.remove('open');
    }
  });
  document.addEventListener('click', () => notifDD.classList.remove('open'));
  notifDD.addEventListener('click', e => e.stopPropagation());
}

// ──────────────────────────────────────────────
// Notifications
// ──────────────────────────────────────────────
const notifIcons = {
  like: { icon: 'fa-heart', color: '#f43f5e' },
  comment: { icon: 'fa-comment', color: '#818cf8' },
  reply: { icon: 'fa-reply', color: '#a78bfa' },
  follow: { icon: 'fa-user-plus', color: '#34d399' },
  mention: { icon: 'fa-at', color: '#fb923c' },
  comment_mention: { icon: 'fa-at', color: '#fb923c' },
};

async function loadNotifications() {
  try {
    const res = await fetch('/notifications/unread/');
    const data = await res.json();
    const badge = document.getElementById('notif-badge');
    const list = document.getElementById('notifList');
    if (!badge || !list) return;

    if (data.count > 0) {
      badge.textContent = data.count > 9 ? '9+' : data.count;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }

    if (data.recent.length === 0) {
      list.innerHTML = '<div class="notif-empty">All caught up! 🎉</div>';
      return;
    }

    list.innerHTML = data.recent.map(n => {
      const meta = notifIcons[n.type] || { icon: 'fa-bell', color: '#818cf8' };
      const link = `/notifications/to/${n.id}/`;
      return `
        <a href="${link}" class="notif-item unread">
          <div style="position:relative">
            ${getAvatar(n.sender, n.avatar, 40)}
            <span style="position:absolute;bottom:-2px;right:-2px;width:16px;height:16px;border-radius:50%;background:${meta.color};display:flex;align-items:center;justify-content:center;border:2px solid #0d1424">
              <i class="fa-solid ${meta.icon}" style="font-size:.5rem;color:white"></i>
            </span>
          </div>
          <div>
            <div class="notif-msg"><strong>${n.sender}</strong> ${n.message}</div>
            <div class="notif-time">${n.created_at}</div>
          </div>
        </a>`;
    }).join('');
  } catch (err) {
    console.error('Notification load error:', err);
  }
}

// Mark all read
document.getElementById('markAllReadBtn')?.addEventListener('click', async () => {
  await fetch('/notifications/mark-read/', { method: 'POST', headers: { 'X-CSRFToken': csrfToken() } });
  document.getElementById('notif-badge').style.display = 'none';
  document.getElementById('notifList').innerHTML = '<div class="notif-empty">All caught up! 🎉</div>';
});

// Poll notifications every 30s
if (document.getElementById('notif-badge')) {
  loadNotifications();
  setInterval(loadNotifications, 30000);
}

// Ping user status every 2 minutes
if (csrfToken()) {
  const pingStatus = () => fetch('/users/ping/', { method: 'GET' });
  pingStatus();
  setInterval(pingStatus, 120000);
}

// ──────────────────────────────────────────────
// Post Creation Form
// ──────────────────────────────────────────────
function toggleExpand(id) {
  document.getElementById(id)?.classList.toggle('open');
}

const privacySelect = document.getElementById('id_privacy');
if (privacySelect) {
  privacySelect.addEventListener('change', function () {
    const block = document.getElementById('specificUsersBlock');
    if (block) block.style.display = this.value === 'specific' ? 'block' : 'none';
  });
}

// ──────────────────────────────────────────────
// Like Button (Post)
// ──────────────────────────────────────────────
document.querySelectorAll('.like-btn').forEach(btn => {
  btn.addEventListener('click', async function () {
    const postId = this.dataset.post;
    const res = await fetch(`/posts/${postId}/like/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken() }
    });
    const data = await res.json();
    const icon = this.querySelector('i');
    const countEl = this.querySelector('.likes-count');

    this.classList.toggle('liked', data.liked);
    icon.className = data.liked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
    if (countEl) countEl.textContent = data.likes_count;

    // Spring animation
    icon.style.transform = 'scale(1.5)';
    setTimeout(() => icon.style.transform = '', 200);

    // Update likers mini-avatars
    const likerBar = document.getElementById(`liker-bar-${postId}`);
    if (likerBar && data.likers) {
      likerBar.innerHTML = data.likers.map(l =>
        l.user__avatar
          ? `<img src="${l.user__avatar}" class="mini-avatar" title="${l.user__username}">`
          : `<div class="mini-avatar">${l.user__username[0].toUpperCase()}</div>`
      ).join('');
    }
  });
});

// ──────────────────────────────────────────────
// Who Liked Modal
// ──────────────────────────────────────────────
async function openLikersModal(postId) {
  const modal = document.getElementById('likersModal');
  const listEl = document.getElementById('likersList');
  modal.style.display = 'flex';
  listEl.innerHTML = '<div class="spinner"></div>';

  const res = await fetch(`/posts/${postId}/likers/`);
  const data = await res.json();
  if (data.likers.length === 0) {
    listEl.innerHTML = '<p style="text-align:center;color:var(--text3);padding:1.5rem">No likes yet</p>';
    return;
  }
  listEl.innerHTML = data.likers.map(l => `
    <div class="liker-row">
      ${l.avatar ? `<img src="${l.avatar}" class="avatar" width="42" height="42">` : `<div class="avatar-fallback" style="width:42px;height:42px;font-size:1rem">${l.username[0].toUpperCase()}</div>`}
      <div>
        <a href="/users/profile/${l.username}/">${l.username}</a>
      </div>
    </div>`).join('');
}

function closeLikersModal() {
  document.getElementById('likersModal').style.display = 'none';
}
document.getElementById('likersModal')?.addEventListener('click', function (e) {
  if (e.target === this) closeLikersModal();
});

// ──────────────────────────────────────────────
// Comments Toggle
// ──────────────────────────────────────────────
document.querySelectorAll('.comment-toggle-btn').forEach(btn => {
  btn.addEventListener('click', function () {
    const postId = this.dataset.post;
    const area = document.getElementById(`comments-area-${postId}`);
    area?.classList.toggle('open');
    if (area?.classList.contains('open')) {
      area.querySelector('.comment-input-field')?.focus();
    }
  });
});

// ──────────────────────────────────────────────
// Submit Comment / Reply
// ──────────────────────────────────────────────
document.querySelectorAll('.comment-form').forEach(form => {
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const postId = this.dataset.post;
    const parentId = this.dataset.parent || null;
    const input = this.querySelector('.comment-input-field');
    const content = input.value.trim();
    if (!content) return;

    const res = await fetch(`/posts/${postId}/comment/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, parent_id: parentId })
    });
    const data = await res.json();
    if (!data.success) return;

    input.value = '';

    const c = data.comment;
    const avatarHtml = getAvatar(c.author, c.avatar, 34);
    const commentHtml = `
      <div class="comment-item" id="comment-${c.id}">
        <div class="status-dot-wrap">${avatarHtml}<span class="status-dot ${c.is_online ? 'online' : ''}"></span></div>
        <div style="flex:1">
          <div class="comment-bubble">
            <div class="comment-author">
              <strong><a href="/users/profile/${c.author}/">${c.author}</a></strong>
              <span>${c.created_at}</span>
            </div>
            <div class="comment-text">${c.content}</div>
            <div class="comment-actions">
              <button class="comment-action-btn" onclick="toggleCommentLike(this, ${c.id})">
                <i class="fa-regular fa-heart"></i> <span>0</span>
              </button>
              <button class="comment-action-btn" onclick="toggleReplyBox(${c.id})">
                <i class="fa-solid fa-reply"></i> Reply
              </button>
            </div>
          </div>
          <div class="reply-composer" id="reply-composer-${c.id}">
            <form class="comment-form" data-post="${postId}" data-parent="${c.id}" style="display:flex;gap:.5rem;flex:1">
              <input type="text" class="comment-input-field" placeholder="Reply to ${c.author}...">
              <button type="submit" class="comment-submit-btn"><i class="fa-solid fa-paper-plane"></i></button>
            </form>
          </div>
          <div class="replies-list" id="replies-${c.id}"></div>
        </div>
      </div>`;

    if (!parentId) {
      const list = document.getElementById(`comment-list-${postId}`);
      const emptyEl = list?.querySelector('.empty-comment-msg');
      emptyEl?.remove();
      if (list) list.insertAdjacentHTML('afterbegin', commentHtml);

      const countEl = document.querySelector(`.comment-toggle-btn[data-post="${postId}"] .comments-count`);
      if (countEl) countEl.textContent = parseInt(countEl.textContent || 0) + 1;
    } else {
      // reply — add to replies section
      const repliesEl = document.getElementById(`replies-${parentId}`);
      if (repliesEl) {
        repliesEl.insertAdjacentHTML('beforeend', `
          <div class="reply-item comment-item" style="margin-top:.5rem">
            <div class="status-dot-wrap">${avatarHtml}<span class="status-dot ${c.is_online ? 'online' : ''}"></span></div>
            <div class="reply-bubble">
              <div class="comment-author"><strong>${c.author}</strong><span>Just now</span></div>
              <div class="comment-text">${c.content}</div>
            </div>
          </div>`);
      }
      // Close reply composer
      document.getElementById(`reply-composer-${parentId}`)?.classList.remove('open');
    }

    // Re-bind new forms
    setupCommentForms();
  });
});

function setupCommentForms() {
  document.querySelectorAll('.comment-form').forEach(form => {
    if (form.__bound) return;
    form.__bound = true;
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      const postId = this.dataset.post;
      const parentId = this.dataset.parent || null;
      const input = this.querySelector('.comment-input-field');
      const content = input.value.trim();
      if (!content) return;
      const res = await fetch(`/posts/${postId}/comment/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, parent_id: parentId })
      });
      const data = await res.json();
      if (!data.success) return;
      input.value = '';
      const c = data.comment;
      if (parentId) {
        const repliesEl = document.getElementById(`replies-${parentId}`);
        const avatarHtml = getAvatar(c.author, c.avatar, 30);
        if (repliesEl) {
          repliesEl.insertAdjacentHTML('beforeend', `
            <div class="reply-item comment-item" style="margin-top:.5rem">
              <div class="status-dot-wrap">${avatarHtml}<span class="status-dot ${c.is_online ? 'online' : ''}"></span></div>
              <div class="reply-bubble">
                <div class="comment-author"><strong>${c.author}</strong><span>Just now</span></div>
                <div class="comment-text">${c.content}</div>
              </div>
            </div>`);
        }
        document.getElementById(`reply-composer-${parentId}`)?.classList.remove('open');
      }
    });
  });
}

// ──────────────────────────────────────────────
// Reply toggle
// ──────────────────────────────────────────────
function toggleReplyBox(commentId) {
  const box = document.getElementById(`reply-composer-${commentId}`);
  box?.classList.toggle('open');
  if (box?.classList.contains('open')) {
    box.querySelector('input')?.focus();
  }
}

// ──────────────────────────────────────────────
// Comment Like
// ──────────────────────────────────────────────
async function toggleCommentLike(btn, commentId) {
  const res = await fetch(`/posts/comment/${commentId}/like/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrfToken() }
  });
  const data = await res.json();
  btn.classList.toggle('liked', data.liked);
  const icon = btn.querySelector('i');
  icon.className = data.liked ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
  btn.querySelector('span').textContent = data.likes_count;
}

// ──────────────────────────────────────────────
// Copy code button
// ──────────────────────────────────────────────
document.querySelectorAll('.copy-code-btn').forEach(btn => {
  btn.addEventListener('click', function () {
    const code = this.closest('.post-code-block').querySelector('code')?.innerText || '';
    navigator.clipboard.writeText(code).then(() => {
      this.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
      setTimeout(() => this.innerHTML = '<i class="fa-solid fa-copy"></i> Copy', 2000);
    });
  });
});

// ──────────────────────────────────────────────
// Follow button (profile page)
// ──────────────────────────────────────────────
const followBtn = document.getElementById('followBtn');
if (followBtn) {
  followBtn.addEventListener('click', async function () {
    const username = this.dataset.username;
    const res = await fetch(`/users/profile/${username}/follow/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken() }
    });
    const data = await res.json();
    const isFollowing = data.following;

    this.innerHTML = isFollowing
      ? '<i class="fa-solid fa-user-minus"></i> Unfollow'
      : '<i class="fa-solid fa-user-plus"></i> Follow';
    this.className = isFollowing ? 'btn btn-outline' : 'btn btn-primary';

    const fc = document.getElementById('follower-count');
    if (fc) fc.textContent = data.followers_count;
  });
}

// ──────────────────────────────────────────────
// Theme Toggle (Dark / Light)
// ──────────────────────────────────────────────
(function initTheme() {
  const saved = localStorage.getItem('snapit-theme') || 'dark';
  applyTheme(saved, false);
})();

function applyTheme(theme, save = true) {
  document.documentElement.setAttribute('data-theme', theme);
  const icon = document.getElementById('themeIcon');
  if (icon) icon.className = theme === 'dark' ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
  if (save) localStorage.setItem('snapit-theme', theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  // Persist to server if logged in
  const csrf = csrfToken();
  if (csrf) {
    fetch('/settings/', {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `action=theme&theme=${next}`
    });
  }
}

// For settings page setTheme function
window.setTheme = function(theme) {
  applyTheme(theme);
  document.getElementById('theme-dark')?.classList.toggle('active', theme === 'dark');
  document.getElementById('theme-light')?.classList.toggle('active', theme === 'light');
};

// ──────────────────────────────────────────────
// Share Modal (global feed share button)
// ──────────────────────────────────────────────
function openShareModal(postId) {
  const url = `${location.origin}/posts/${postId}/`;
  const modal = document.getElementById('shareModal');
  const input = document.getElementById('shareUrlInput');
  if (!modal || !input) {
    // fallback
    if (navigator.share) navigator.share({ title: 'SnapIt Post', url });
    else navigator.clipboard.writeText(url).then(() => showGlobalToast('Link copied!'));
    return;
  }
  input.value = url;
  modal.style.display = 'flex';

  const platforms = document.getElementById('sharePlatforms');
  if (platforms) {
    const options = [
      { name: 'Twitter', icon: 'fa-brands fa-x-twitter', color: '#1d9bf0', href: `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}` },
      { name: 'WhatsApp', icon: 'fa-brands fa-whatsapp', color: '#25d366', href: `https://wa.me/?text=${encodeURIComponent(url)}` },
      { name: 'Telegram', icon: 'fa-brands fa-telegram', color: '#26a5e4', href: `https://t.me/share/url?url=${encodeURIComponent(url)}` },
    ];
    platforms.innerHTML = options.map(o => `
      <a href="${o.href}" target="_blank" class="btn btn-ghost btn-sm" style="gap:.5rem;border-color:${o.color}20;color:${o.color}">
        <i class="${o.icon}"></i> ${o.name}
      </a>`).join('');
  }
}

function copyShareUrl() {
  const input = document.getElementById('shareUrlInput');
  if (!input) return;
  navigator.clipboard.writeText(input.value).then(() => {
    showGlobalToast('Link copied to clipboard!');
    document.getElementById('shareModal').style.display = 'none';
  });
}

function showGlobalToast(msg, type = 'success') {
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${msg} <button onclick="this.parentElement.remove()"><i class="fa-solid fa-xmark"></i></button>`;
  let tc = document.getElementById('toastContainer');
  if (!tc) {
    tc = document.createElement('div');
    tc.className = 'toast-container';
    tc.id = 'toastContainer';
    document.body.appendChild(tc);
  }
  tc.appendChild(t);
  setTimeout(() => t.remove(), 4500);
}

// Close share modal on backdrop click
document.getElementById('shareModal')?.addEventListener('click', function(e) {
  if (e.target === this) this.style.display = 'none';
});

// ──────────────────────────────────────────────
// Message Badge Polling
// ──────────────────────────────────────────────
async function pollMessageCount() {
  try {
    const res = await fetch('/messages/unread/');
    const data = await res.json();
    const badge = document.getElementById('msg-badge');
    if (!badge) return;
    if (data.count > 0) {
      badge.textContent = data.count > 9 ? '9+' : data.count;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
    }
  } catch {}
}

if (document.getElementById('msg-badge')) {
  pollMessageCount();
  setInterval(pollMessageCount, 20000);
}

// ──────────────────────────────────────────────
// Live User Search
// ──────────────────────────────────────────────
const globalSearch = document.getElementById('globalSearch');
const searchResults = document.getElementById('searchResults');
let searchTimeout;

if (globalSearch && searchResults) {
  globalSearch.addEventListener('input', function() {
    clearTimeout(searchTimeout);
    const q = this.value.trim();
    if (!q) { searchResults.classList.remove('open'); return; }
    searchTimeout = setTimeout(async () => {
      try {
        const res = await fetch(`/users/search/?q=${encodeURIComponent(q)}`);
        if (!res.ok) return;
        const data = await res.json();
        if (!data.users?.length) { searchResults.classList.remove('open'); return; }
        searchResults.innerHTML = data.users.map(u => `
          <a href="/users/profile/${u.username}/" class="search-result-item">
            ${u.avatar ? `<img src="${u.avatar}" class="avatar" width="36" height="36">` : `<div class="avatar-fallback" style="width:36px;height:36px;font-size:.9rem">${u.username[0].toUpperCase()}</div>`}
            <div>
              <div style="font-weight:600">${u.username}</div>
              <div style="font-size:.75rem;color:var(--text3)">${u.bio || ''}</div>
            </div>
            ${u.is_online ? '<span class="badge badge-success" style="margin-left:auto;font-size:.65rem">Online</span>' : ''}
          </a>`).join('');
        searchResults.classList.add('open');
      } catch {}
    }, 350);
  });
  document.addEventListener('click', e => {
    if (!globalSearch.contains(e.target)) searchResults.classList.remove('open');
  });
}

// ──────────────────────────────────────────────
// Report System (Global)
// ──────────────────────────────────────────────
window._reportTarget = { username: null, postId: null };

window.openReportModal = function(username, postId) {
  window._reportTarget = { username, postId };
  const modal = document.getElementById('reportModal');
  if (modal) {
    modal.style.display = 'flex';
    // init custom selects inside modal if not yet
    if (typeof initCustomSelects === 'function') initCustomSelects();
  }
};

window.closeReportModal = function() {
  const modal = document.getElementById('reportModal');
  if (modal) modal.style.display = 'none';
};

document.getElementById('reportModal')?.addEventListener('click', function(e) {
  if (e.target === this) window.closeReportModal();
});

window.submitReport = async function() {
  const payload = {
    username: window._reportTarget.username,
    post_id: window._reportTarget.postId,
    reason: document.getElementById('reportReason').value,
    description: document.getElementById('reportDesc').value,
  };
  const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value 
                || document.querySelector('#csrf-holder input')?.value 
                || '';
                
  const res = await fetch('/settings/report/', {
    method: 'POST',
    headers: { 'X-CSRFToken': token, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  window.closeReportModal();
  if (typeof showGlobalToast === 'function') {
    showGlobalToast(data.message || 'Report submitted!', data.ok ? 'success' : 'error');
  } else {
    alert(data.message || 'Report submitted!');
  }
};

// ──────────────────────────────────────────────
// To-Do List APIs
// ──────────────────────────────────────────────
window.addTodo = async function() {
  const input = document.getElementById('todoInput');
  const text = input.value.trim();
  if (!text) return;
  
  const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value || document.querySelector('#csrf-holder input')?.value || '';
  const res = await fetch('/api/todo/add/', {
    method: 'POST',
    headers: { 'X-CSRFToken': token, 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  const data = await res.json();
  if (data.ok) {
    input.value = '';
    const emptyMsg = document.getElementById('todoEmptyMsg');
    if (emptyMsg) emptyMsg.remove();
    
    document.getElementById('todoList').insertAdjacentHTML('afterbegin', `
      <div class="todo-item" id="todo-${data.id}" style="display:flex;align-items:flex-start;gap:.6rem;padding:.5rem;background:var(--surface2);border-radius:8px">
        <input type="checkbox" onchange="toggleTodo(${data.id})" style="margin-top:.2rem;cursor:pointer">
        <span style="flex:1;font-size:.85rem;color:var(--text);word-break:break-word;">${data.text.replace(/</g, "&lt;")}</span>
        <button class="btn-link" style="color:var(--danger);font-size:.8rem;padding:0" onclick="deleteTodo(${data.id})"><i class="fa-solid fa-trash-can"></i></button>
      </div>`);
  }
};

window.toggleTodo = async function(id) {
  const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value || document.querySelector('#csrf-holder input')?.value || '';
  const res = await fetch(`/api/todo/${id}/toggle/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': token }
  });
  const data = await res.json();
  if (data.ok) {
    const el = document.getElementById(`todo-${id}`);
    const span = el.querySelector('span');
    if (data.is_completed) {
      el.classList.add('completed');
      span.style.textDecoration = 'line-through';
      span.style.color = 'var(--text3)';
    } else {
      el.classList.remove('completed');
      span.style.textDecoration = 'none';
      span.style.color = 'var(--text)';
    }
  }
};

window.deleteTodo = async function(id) {
  const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value || document.querySelector('#csrf-holder input')?.value || '';
  const res = await fetch(`/api/todo/${id}/delete/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': token }
  });
  const data = await res.json();
  if (data.ok) {
    document.getElementById(`todo-${id}`).remove();
    if (document.querySelectorAll('.todo-item').length === 0) {
      document.getElementById('todoList').innerHTML = '<div id="todoEmptyMsg" style="font-size:.8rem;color:var(--text3);text-align:center;padding:.5rem 0">No tasks yet.</div>';
    }
  }
};
