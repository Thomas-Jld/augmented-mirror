const io = require('socket.io')(5000);

let reflection = {};

io.on('connect', socket => {
  // either with send()
  console.log(socket);

  // or with emit() and custom event names
  socket.emit('greetings', "Hi !");

  // handle the event sent with socket.send()
  socket.on('reflection', (data) => {
    reflection = data;
  });

  socket.on('next', (data) => {
    socket.emit('update', reflection);
  })

});
