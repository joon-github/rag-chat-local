// frontend/main.js
const { app, BrowserWindow, dialog, ipcMain } = require("electron");
const os = require("os");
const path = require("path");
const { spawn } = require("child_process");
const treeKill = require("tree-kill");
const { join } = require("path");

let pyProc = null;
const isWindows = os.platform() === "win32";
function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
  });
  win.loadFile(path.join(__dirname, "index.html"));
}

ipcMain.handle("select-folder", async () => {
  const result = await dialog.showOpenDialog({
    properties: ["openDirectory"],
    defaultPath: app.getPath("home"), // 홈 디렉토리로 시작
  });
  console.log("result", result);
  if (result.canceled || result.filePaths.length === 0) {
    console.log("🛑 사용자 취소");
    return null;
  }

  console.log("📂 선택된 폴더:", result.filePaths[0]);
  return result.filePaths[0];
});

function startPythonServer() {
  const venvPythonMac = path.join(__dirname, "../backend/venv/bin/python"); // macOS/Linux
  const venvPythonWin = path.join(
    __dirname,
    "../backend/venv/Scripts/python.exe"
  ); // Windows

  const venvPython = isWindows ? venvPythonWin : venvPythonMac;

  pyProc = spawn(
    venvPython,
    ["-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
    {
      cwd: path.join(__dirname, "../backend"),
      shell: true,
    }
  );

  pyProc.stdout.on("data", (data) => {
    console.log(`PYTHON: ${data}`);
  });

  pyProc.stderr.on("data", (data) => {
    console.error(`PYTHON ERR: ${data}`);
  });

  const execPath = isWindows
    ? path.join(process.resourcesPath, "backend/dist/fastapi-server.exe")
    : path.join(process.resourcesPath, "backend/dist/fastapi-server");
  pyProc = spawn(execPath, [], {
    shell: true,
  });
}

setInterval(() => {
  fetch("http://127.0.0.1:8000/ping").catch(() => {
    console.log("❌ 서버에 ping 실패");
  });
}, 10_000); // 10초마다 ping

app.whenReady().then(() => {
  createWindow();
  startPythonServer();
});

app.on("before-quit", () => {
  if (pyProc) {
    treeKill(pyProc.pid, "SIGKILL");
  }
});

app.on("will-quit", () => {
  if (pyProc) pyProc.kill();
});
