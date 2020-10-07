const io = require('socket.io')(5000);

io.on('connect', socket => {
  // either with send()
  console.log(socket);

  socket.send('Hello!');

  // or with emit() and custom event names
  socket.emit('greetings', "Hi !";

  // handle the event sent with socket.send()
  socket.on('reflection', (data) => {
    console.log(data);
  });

  // handle the event sent with socket.emit()
  socket.on('salutations', (elem1, elem2, elem3) => {
    console.log(elem1, elem2, elem3);
  });
});
