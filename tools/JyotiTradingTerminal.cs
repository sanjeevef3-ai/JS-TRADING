using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Threading;
using System.Windows.Forms;

namespace JyotiTrading
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            string baseDir = @"d:\AGI";
            string pythonw = Path.Combine(baseDir, @".venv\Scripts\pythonw.exe");
            string serverPy = Path.Combine(baseDir, "server.py");
            string targetUrl = "http://127.0.0.1:8000/";

            // 1. Check if backend is alive
            bool isServerUp = CheckServerAlive(targetUrl);
            if (!isServerUp)
            {
                // Start Python backend silently
                ProcessStartInfo pyStart = new ProcessStartInfo
                {
                    FileName = pythonw,
                    Arguments = string.Format("\"{0}\"", serverPy),
                    WorkingDirectory = baseDir,
                    CreateNoWindow = true,
                    UseShellExecute = false,
                    WindowStyle = ProcessWindowStyle.Hidden
                };
                try
                {
                    Process.Start(pyStart);
                }
                catch { }

                // Wait up to 10 seconds for server to boot
                for (int i = 0; i < 20; i++)
                {
                    Thread.Sleep(500);
                    if (CheckServerAlive(targetUrl))
                    {
                        isServerUp = true;
                        break;
                    }
                }
            }

            // 1.5 Ensure Permanent Ngrok Tunnel is running silently in background
            string ngrokExe = Path.Combine(baseDir, @"tools\ngrok.exe");
            if (File.Exists(ngrokExe) && Process.GetProcessesByName("ngrok").Length == 0)
            {
                ProcessStartInfo ngrokStart = new ProcessStartInfo
                {
                    FileName = ngrokExe,
                    Arguments = "http 8000 --url https://pastrami-troubling-heave.ngrok-free.dev",
                    WorkingDirectory = baseDir,
                    CreateNoWindow = true,
                    UseShellExecute = false,
                    WindowStyle = ProcessWindowStyle.Hidden
                };
                try { Process.Start(ngrokStart); } catch { }
            }

            // 2. Launch Dedicated Desktop Trading Window via Edge or Chrome App Mode
            string edgePath = @"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe";
            if (!File.Exists(edgePath))
                edgePath = @"C:\Program Files\Microsoft\Edge\Application\msedge.exe";

            string chromePath = @"C:\Program Files\Google\Chrome\Application\chrome.exe";
            if (!File.Exists(chromePath))
                chromePath = @"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe";

            string browserExe = null;
            if (File.Exists(edgePath)) browserExe = edgePath;
            else if (File.Exists(chromePath)) browserExe = chromePath;

            if (browserExe != null)
            {
                ProcessStartInfo appStart = new ProcessStartInfo
                {
                    FileName = browserExe,
                    Arguments = string.Format("--app=\"{0}\" --window-size=1400,900 --start-maximized", targetUrl),
                    UseShellExecute = true
                };
                Process.Start(appStart);
            }
            else
            {
                // Fallback to default browser
                Process.Start(new ProcessStartInfo(targetUrl) { UseShellExecute = true });
            }
        }

        static bool CheckServerAlive(string url)
        {
            try
            {
                HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);
                req.Timeout = 1500;
                req.Method = "GET";
                using (HttpWebResponse res = (HttpWebResponse)req.GetResponse())
                {
                    return res.StatusCode == HttpStatusCode.OK;
                }
            }
            catch
            {
                return false;
            }
        }
    }
}
