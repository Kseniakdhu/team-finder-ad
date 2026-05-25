// Project-specific JS (complete project action + toggle participate + toggle favorite)
(function(){
  document.addEventListener("DOMContentLoaded", function() {
    const completeBtn = document.getElementById("complete-project-btn");
    if (completeBtn) {
      completeBtn.addEventListener("click", function(e) {
        e.preventDefault();
        const projectId = completeBtn.dataset.id;
        if (!projectId) return;

        fetch(`/projects/${projectId}/complete/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": window.getCookie ? window.getCookie("csrftoken") : "",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === "ok") {
            const statusEl = document.querySelector(".project-status-black");
            if (statusEl) statusEl.textContent = "Закрыт";
            completeBtn.remove();
            if (window.toast) window.toast("Проект завершён", { type: 'info' });
          } else {
            if (window.toast) window.toast("Ошибка при завершении проекта", { type: 'error' });
            else alert("Ошибка при завершении проекта");
          }
        })
        .catch(err => {
          console.error("Ошибка запроса:", err);
          if (window.toast) window.toast("Ошибка сети", { type: 'error' });
        });
      });
    }

    const participateBtn = document.getElementById("participate-btn");
    const participantsList = document.getElementById("participants-list");
    const participantsCount = document.getElementById("participants-count");
    if (participateBtn && participantsList && participantsCount) {
      const userId = participateBtn.dataset.userId || null;
      const projectId = participateBtn.dataset.project;
      const userName = participateBtn.dataset.userName || "";
      const userAvatar = participateBtn.dataset.userAvatar || "";

      participateBtn.addEventListener("click", function(e) {
        e.preventDefault();
        if (!projectId) return;

        fetch(`/projects/${projectId}/toggle-participate/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": window.getCookie ? window.getCookie("csrftoken") : "",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({})
        })
        .then(resp => resp.json())
        .then(data => {
          if (data.status !== "ok") {
            if (window.toast) window.toast("Ошибка при изменении участия", { type: 'error' });
            else alert("Ошибка при изменении участия");
            return;
          }

          if (data.participant) {
            participateBtn.textContent = "Отказаться от участия";

            const noParticipants = document.getElementById("no-participants");
            if (noParticipants) noParticipants.remove();

            const a = document.createElement("a");
            a.href = `/users/${userId}`;
            a.id = `participant-${userId}`;
            a.innerHTML = `
              <div class="participant-item">
                <img src="${userAvatar}" alt="Аватар" class="participant-avatar">
                <div class="participant-info">
                  <span class="participant-name">${userName}</span>
                  <span class="participant-role">Участник</span>
                </div>
              </div>
            `;
            participantsList.appendChild(a);

            participantsCount.textContent = parseInt(participantsCount.textContent) + 1;

          } else {
            participateBtn.textContent = "Участвовать";

            const el = document.getElementById(`participant-${userId}`);
            if (el) el.remove();

            const newCount = parseInt(participantsCount.textContent) - 1;
            participantsCount.textContent = newCount;

            if (newCount === 0) {
              const p = document.createElement("p");
              p.id = "no-participants";
              p.textContent = "Пока нет участников";
              participantsList.appendChild(p);
            }
          }
        })
        .catch(err => {
          console.error("Ошибка запроса:", err);
          if (window.toast) window.toast("Ошибка сети", { type: 'error' });
        });
      });
    }

    const favoriteBtn = document.getElementById("favorite-btn");
    if (favoriteBtn) {
      const projectId = favoriteBtn.dataset.project;

      // SVG иконки
      const starSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>`;
      const starFilledSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>`;

      favoriteBtn.addEventListener("click", function(e) {
        e.preventDefault();
        if (!projectId) return;

        fetch(`/projects/${projectId}/toggle-favorite/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": window.getCookie ? window.getCookie("csrftoken") : "",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({})
        })
        .then(resp => resp.json())
        .then(data => {
          if (data.status !== "ok") {
            if (window.toast) window.toast("Ошибка при изменении избранного", { type: 'error' });
            else alert("Ошибка при изменении избранного");
            return;
          }

          if (data.is_favorite) {
            favoriteBtn.innerHTML = starFilledSvg + ' В избранном';
            if (window.toast) window.toast("Добавлено в избранное", { type: 'success' });
          } else {
            favoriteBtn.innerHTML = starSvg + ' В избранное';
            if (window.toast) window.toast("Удалено из избранного", { type: 'info' });
          }
        })
        .catch(err => {
          console.error("Ошибка запроса:", err);
          if (window.toast) window.toast("Ошибка сети", { type: 'error' });
        });
      });
    }
  });
})();
