const BASE_URL = "https://devsage-9qlh.onrender.com";
const EXTENSION_SECRET = "ds_secure_2026";

export async function analyzeCode(
  code: string,
  language: string,
  mode: string,
  projectPath?: string
) {
  const response = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-extension-key": EXTENSION_SECRET,
    },
    body: JSON.stringify({
      code,
      language,
      mode,
      project_path: projectPath || null,
    }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    console.error("DevSage analyze error:", err);
    throw new Error("Backend error occurred.");
  }

  return await response.json();
}

export async function requestAIFix(
  code: string,
  language: string,
  issue: string
) {
  const response = await fetch(`${BASE_URL}/fix`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-extension-key": EXTENSION_SECRET,
    },
    body: JSON.stringify({
      code,
      language,
      issue,
    }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    console.error("DevSage fix error:", err);
    throw new Error("AI fix failed.");
  }

  return await response.json();
}