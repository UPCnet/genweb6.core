// @@netejar_metadades
// Font: es minifica a genweb6.theme (js/views/netejar_metadades.min.js)

document.addEventListener('DOMContentLoaded', function() {
  var section = document.querySelector('.netejar-metadades');

  // Després d'iniciar sessió dins l'iframe, recarreguem la pàgina que el conté
  if (section && section.dataset.reloadParent && window.self !== window.top) {
    window.top.location.reload();
  }

  var form = document.getElementById('upc-form');
  var spinner = document.getElementById('spinner');
  var submitBtn = document.getElementById('netejar-btn');
  var fileInput = document.getElementById('pdf_file');
  var originalBtnText = submitBtn ? submitBtn.textContent : 'Netejar';
  var alertShown = false;

  function resetForm() {
    submitBtn.textContent = originalBtnText;
    spinner.style.display = 'none';
    submitBtn.disabled = false;
    submitBtn.style.opacity = '1';
    submitBtn.style.cursor = 'pointer';
    fileInput.style.pointerEvents = 'auto';
    fileInput.style.opacity = '1';
    fileInput.value = '';
    alertShown = false;
  }

  if (form) {
    form.addEventListener('submit', function(e) {
      submitBtn.textContent = 'Netejant...';
      spinner.style.display = 'inline-block';
      submitBtn.disabled = true;
      submitBtn.style.opacity = '0.6';
      submitBtn.style.cursor = 'not-allowed';
      fileInput.style.pointerEvents = 'none';
      fileInput.style.opacity = '0.6';
      alertShown = false;

      setTimeout(function() {
        if (!alertShown) {
          alert('El PDF sense metadades es descarregarà en breu. Pot tardar uns minuts.');
          alertShown = true;
        }
      }, 3000);

      setTimeout(function() {
        resetForm();
      }, 30000);
    });
  }
});
