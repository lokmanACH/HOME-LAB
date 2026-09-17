const expree =require('express');
const app = expree();
const port = 3100;

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(port, () => {
  console.log(`Example app listening at port ${port}`);
});