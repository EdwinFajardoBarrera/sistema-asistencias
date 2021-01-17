// console.log("Estatico");

let train = document.querySelector('#train')
let register = document.querySelector('#register')
let cancel = document.querySelector('#modalCancel')
let send = document.querySelector('#send')

//ENTRENAMIENTO
train.addEventListener('click', (event) => {
  console.log('Se hizo click en el boton entrena');

  Swal.fire({
    title: 'Entrenamiento del sistema de reconocimiento',
    confirmButtonText: 'Entrenar',
    width: '30%',
    showLoaderOnConfirm: true,
    preConfirm: () => {
      return fetch(`/train`)
        .then(response => {
          return
        })
        .catch(error => {
          Swal.showValidationMessage(
            `Request failed: ${error}`
          )
        })
    },
    allowOutsideClick: () => !Swal.isLoading()
  }).then((result) => {
    if (result.isConfirmed) {
      Swal.fire({
        position: 'center',
        icon: 'success',
        html: '<h2>¡Sistema entrenado con éxito!</h2>',
        showConfirmButton: false,
        timer: 2000,
        width: '30%'
      })
    }
  })
})

register.addEventListener('click', (event) => {
  console.log('Se hizo click en el boton registrar');
  let p = document.getElementById('modal');
  p.removeAttribute("hidden");
})

cancel.addEventListener('click', (event) => {
  console.log('Se hizo click en el boton cancelar');
  let p = document.getElementById('modal');
  p.setAttribute("hidden", true);
})

send.addEventListener('click', (event) => {
  console.log('Se hizo click en el boton enviar');
  let name = document.getElementById("name").value
  let birthday = document.getElementById("birthday").value

  console.log(`El nombre es: ${name} y el cumpleaños es: ${birthday}`);

  fetch("/register_user", {
    method: 'POST', // or 'PUT'
    body: JSON.stringify({ name: name, birthday: birthday }),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(res => res.json())
    .catch(error => console.error('Error:', error))
    .then(response => {

      console.log('Success:', response)
      window.location.href = `/register_face/${response.userName}`
    });

})