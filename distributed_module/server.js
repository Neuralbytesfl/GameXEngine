const net = require('net');
const fs = require('fs');
const path = require('path');

const PORT = 9999;
const ADDRESS = '0.0.0.0';

let fileStore = {}; // Object to store file data in RAM

const server = net.createServer((socket) => {
  console.log('Client connected:', socket.remoteAddress);

  let request = '';
  let receivingFile = false;
  let fileBuffer = Buffer.alloc(0);
  let fileSize = 0;
  let receivedSize = 0;
  let fileName = '';

  socket.on('data', (data) => {
    if (!receivingFile) {
      // First part of data is JSON header
      request += data.toString();

      try {
        const jsonIndex = request.indexOf('\r\n\r\n');
        if (jsonIndex !== -1) {
          const jsonData = request.substring(0, jsonIndex);
          request = request.substring(jsonIndex + 4); // Remove JSON part
          const parsedRequest = JSON.parse(jsonData);

          if (parsedRequest.operation === 'UPLOAD') {
            fileName = parsedRequest.fileName;
            fileSize = parsedRequest.fileSize;
            receivingFile = true;
            fileBuffer = Buffer.alloc(fileSize);
            receivedSize = 0;
            console.log(`Receiving file '${fileName}' of size ${fileSize} bytes`);
          } else if (parsedRequest.operation === 'DOWNLOAD') {
            if (fileStore[parsedRequest.fileName]) {
              let fileData = fileStore[parsedRequest.fileName];
              let chunkSize = 64 * 1024; // 64 KB
              let offset = 0;

              // Send file size header
              const header = JSON.stringify({ fileSize: fileData.length });
              socket.write(header + '\r\n\r\n');

              function sendNextChunk() {
                if (offset < fileData.length) {
                  let chunk = fileData.slice(offset, offset + chunkSize);
                  socket.write(chunk);
                  offset += chunk.length;
                  console.log(`Sending '${parsedRequest.fileName}': ${((offset / fileData.length) * 100).toFixed(2)}% complete`);
                  setImmediate(sendNextChunk); // Use setImmediate to avoid blocking the event loop
                } else {
                  socket.end();
                  console.log(`Download of '${parsedRequest.fileName}' completed`);
                }
              }

              sendNextChunk();
            } else {
              socket.write('File not found');
              socket.end();
            }
          }
        }
      } catch (e) {
        console.error('Failed to parse request:', e);
        socket.end();
        return;
      }
    } else {
      // Process binary data for file
      fileBuffer.fill(data, receivedSize, receivedSize + data.length);
      receivedSize += data.length;

      if (receivedSize >= fileSize) {
        receivingFile = false;
        fileStore[fileName] = fileBuffer;
        console.log(`Upload completed: '${fileName}'`);
        socket.end();
      }
    }
  });

  socket.on('error', (err) => {
    console.error('Socket error:', err);
  });

  socket.on('end', () => {
    console.log('Client disconnected');
  });
});

server.listen(PORT, ADDRESS, () => {
  console.log(`Server listening on ${ADDRESS}:${PORT}`);
});
