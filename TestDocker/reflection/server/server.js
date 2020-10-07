const io = require('socket.io')(5000);


io.on('connect', socket => {
  // either with send()
  console.log(socket);

  socket.send('Hello!');

  // or with emit() and custom event names
  socket.emit('greetings', "Hi !");

  // handle the event sent with socket.send()
  socket.on('message', (data) => {
    console.log(data);
  });

});
