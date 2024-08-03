const net = require('net');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const [,, serverIP, serverPort, operation, filePath] = process.argv;

const client = new net.Socket();
client.connect(serverPort, serverIP, () => {
  console.log(`Connected to server ${serverIP}:${serverPort}`);

  const startTime = Date.now();

  if (operation === 'UPLOAD') {
    // Upload file
    fs.stat(filePath, (err, stats) => {
      if (err) {
        console.error('Error reading file:', err);
        client.end();
        return;
      }

      const fileName = path.basename(filePath);
      const fileSize = stats.size;

      // Compute SHA256 hash
      const hash = crypto.createHash('sha256');
      const fileStream = fs.createReadStream(filePath);

      fileStream.on('data', (chunk) => hash.update(chunk));
      fileStream.on('end', () => {
        const fileHash = hash.digest('hex');
        const request = JSON.stringify({ operation, fileName, fileSize, fileHash });

        client.write(request + '\r\n\r\n'); // End JSON header with double CRLF

        const uploadStream = fs.createReadStream(filePath);
        let sentSize = 0;
        const chunkSize = 64 * 1024; // 64 KB
        let lastUpdateTime = startTime;
        let lastSentSize = 0;

        uploadStream.on('data', (chunk) => {
          const now = Date.now();
          const elapsedTime = (now - startTime) / 1000; // seconds
          const chunkTime = (now - lastUpdateTime) / 1000; // seconds
          const speed = (sentSize - lastSentSize) / chunkTime / 1024; // KB/s
          const remainingSize = fileSize - sentSize;
          const estimatedTime = (remainingSize / (speed * 1024)) || 0; // seconds
          lastUpdateTime = now;
          lastSentSize = sentSize;

          client.write(chunk);
          sentSize += chunk.length;
          const progress = (sentSize / fileSize) * 100;

          console.log(`Uploading '${fileName}': ${progress.toFixed(2)}% complete`);
          console.log(`Speed: ${speed.toFixed(2)} KB/s`);
          console.log(`Estimated time remaining: ${estimatedTime.toFixed(2)} seconds`);
        });

        uploadStream.on('end', () => {
          const totalTime = (Date.now() - startTime) / 1000; // seconds
          console.log(`Upload of '${fileName}' completed`);
          console.log(`Total time taken: ${totalTime.toFixed(2)} seconds`);
          client.end();
        });

        uploadStream.on('error', (err) => {
          console.error('Error reading file:', err);
          client.end();
        });
      });
    });
  } else if (operation === 'DOWNLOAD') {
    // Download file
    const fileName = path.basename(filePath);
    const request = JSON.stringify({ operation, fileName });

    client.write(request + '\r\n\r\n'); // End JSON header with double CRLF

    const fileStream = fs.createWriteStream(filePath);
    let receivedSize = 0;
    let fileSize = 0;
    let startTime = null;
    let lastUpdateTime = Date.now();
    let lastReceivedSize = 0;

    client.on('data', (chunk) => {
      if (fileSize === 0) {
        // Handle header received before file data
        try {
          const headerEndIndex = chunk.indexOf('\r\n\r\n');
          if (headerEndIndex !== -1) {
            const header = chunk.slice(0, headerEndIndex).toString();
            const { fileSize: size } = JSON.parse(header);
            fileSize = size;
            startTime = Date.now();
            console.log(`Downloading '${fileName}' of size ${fileSize} bytes`);
            fileStream.write(chunk.slice(headerEndIndex + 4)); // Write the data part
          }
        } catch (e) {
          console.error('Failed to parse header:', e);
          client.end();
        }
      } else {
        fileStream.write(chunk);
      }

      receivedSize += chunk.length;
      const elapsedTime = (Date.now() - startTime) / 1000; // seconds
      const progress = (receivedSize / fileSize) * 100;
      const speed = (receivedSize / elapsedTime / 1024).toFixed(2); // KB/s
      const remainingSize = fileSize - receivedSize;
      const estimatedTime = (remainingSize / (speed * 1024)) || 0; // seconds

      console.log(`Downloading '${fileName}': ${progress.toFixed(2)}% complete`);
      console.log(`Speed: ${speed} KB/s`);
      console.log(`Estimated time remaining: ${estimatedTime.toFixed(2)} seconds`);
    });

    client.on('end', () => {
      fileStream.end();
      const totalTime = (Date.now() - startTime) / 1000; // seconds
      console.log(`Download of '${fileName}' completed`);
      console.log(`Total time taken: ${totalTime.toFixed(2)} seconds`);
    });

    client.on('error', (err) => {
      console.error('Socket error:', err);
    });

    fileStream.on('error', (err) => {
      console.error('File stream error:', err);
      client.end();
    });
  } else if (operation === 'LIST') {
    // List files
    client.write(JSON.stringify({ operation }) + '\r\n\r\n');

    client.on('data', (data) => {
      console.log('File list:', data.toString());
      client.end();
    });

    client.on('error', (err) => {
      console.error('Socket error:', err);
    });
  }
});
