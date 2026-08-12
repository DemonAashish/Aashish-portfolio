(function () {
  'use strict';

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $all(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }

  function esc(str) {
    const div = document.createElement('div');
    div.textContent = str == null ? '' : String(str);
    return div.innerHTML;
  }

  // ---- footer year ----
  const yearEl = $('#year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // ---- mobile nav ----
  const navToggle = $('#navToggle');
  const navMobile = $('#navMobile');
  if (navToggle && navMobile) {
    navToggle.addEventListener('click', () => {
      const isOpen = navMobile.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(isOpen));
    });
    $all('a', navMobile).forEach((a) =>
      a.addEventListener('click', () => {
        navMobile.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
      })
    );
  }

  // ---- scroll reveal for each stop ----
  const stops = $all('.stop');
  if ('IntersectionObserver' in window && stops.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -60px 0px' }
    );
    stops.forEach((stop) => observer.observe(stop));
    // Safety net: if anything is still unrevealed after 2.5s (observer
    // didn't fire for some reason), just show it rather than leaving it hidden.
    setTimeout(() => stops.forEach((stop) => stop.classList.add('is-visible')), 2500);
  } else {
    stops.forEach((stop) => stop.classList.add('is-visible'));
  }

  // ---- route-line "traveled" progress fill ----
  const journey = $('.journey');
  const fill = $('#journeyFill');
  if (journey && fill) {
    let ticking = false;
    const updateFill = () => {
      const rect = journey.getBoundingClientRect();
      const total = rect.height;
      const viewed = Math.min(Math.max(-rect.top + window.innerHeight * 0.5, 0), total);
      const pct = total > 0 ? (viewed / total) * 100 : 0;
      fill.style.height = pct + '%';
      ticking = false;
    };
    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(updateFill);
        ticking = true;
      }
    };
    updateFill();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', updateFill);
  }

  // ---- contact form ----
  const contactForm = $('#contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = $('#cfSubmit');
      const status = $('#cfStatus');
      const payload = {
        name: $('#cf-name').value.trim(),
        email: $('#cf-email').value.trim(),
        subject: $('#cf-subject').value.trim(),
        message: $('#cf-message').value.trim(),
      };

      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending…';
      status.textContent = '';
      status.className = 'form-status';

      try {
        const res = await fetch('/api/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Something went wrong.');
        status.textContent = data.message || 'Thanks — message sent!';
        status.className = 'form-status form-status--ok';
        contactForm.reset();
      } catch (err) {
        status.textContent = err.message;
        status.className = 'form-status form-status--error';
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send Message';
      }
    });
  }

  // ---- AI chat widget ----
  const launcher = $('#chatLauncher');
  const panel = $('#chatPanel');
  const closeBtn = $('#chatClose');
  const chatForm = $('#chatForm');
  const chatInput = $('#chatInput');
  const chatBody = $('#chatBody');
  const chatSend = $('#chatSend');

  const sessionId = 'sess-' + Math.random().toString(36).slice(2) + Date.now().toString(36);

  function appendMessage(text, who) {
    const div = document.createElement('div');
    div.className = 'chat-msg chat-msg--' + who;
    div.innerHTML = esc(text).replace(/\n/g, '<br>');
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
    return div;
  }

  function appendTyping() {
    const div = document.createElement('div');
    div.className = 'chat-msg chat-msg--typing';
    div.innerHTML = '<span></span><span></span><span></span>';
    chatBody.appendChild(div);
    chatBody.scrollTop = chatBody.scrollHeight;
    return div;
  }

  if (launcher && panel) {
    launcher.addEventListener('click', () => {
      const isOpen = panel.classList.toggle('is-open');
      launcher.setAttribute('aria-expanded', String(isOpen));
      if (isOpen) chatInput.focus();
    });
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        panel.classList.remove('is-open');
        launcher.setAttribute('aria-expanded', 'false');
      });
    }
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && panel.classList.contains('is-open')) {
        panel.classList.remove('is-open');
        launcher.setAttribute('aria-expanded', 'false');
      }
    });
  }

  if (chatForm) {
    chatForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (!message) return;

      appendMessage(message, 'user');
      chatInput.value = '';
      chatInput.disabled = true;
      chatSend.disabled = true;
      const typingEl = appendTyping();

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: message, session_id: sessionId }),
        });
        const data = await res.json();
        typingEl.remove();
        if (!res.ok) throw new Error(data.error || 'Something went wrong.');
        appendMessage(data.reply, 'bot');
      } catch (err) {
        typingEl.remove();
        appendMessage('Sorry, something went wrong reaching the AI service. Please try again.', 'bot');
      } finally {
        chatInput.disabled = false;
        chatSend.disabled = false;
        chatInput.focus();
      }
    });
  }
})();
