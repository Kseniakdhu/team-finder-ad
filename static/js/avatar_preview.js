document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('id_avatar');
    const img = document.querySelector('.avatar-preview img');
    if (!input || !img) return;

    input.addEventListener('change', function() {
        const file = input.files && input.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(ev) {
            img.src = ev.target.result;
        };
        reader.readAsDataURL(file);
    });
});
