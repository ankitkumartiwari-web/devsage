import * as vscode from "vscode";
import { analyzeCode, requestAIFix } from "./api";

let diagnosticCollection: vscode.DiagnosticCollection;
let latestResult: any = null;
let isRequestRunning = false;

export function activate(context: vscode.ExtensionContext) {

  diagnosticCollection =
    vscode.languages.createDiagnosticCollection("devsage");

  context.subscriptions.push(diagnosticCollection);

  // =========================================================
  // REVIEW COMMAND
  // =========================================================

  context.subscriptions.push(
    vscode.commands.registerCommand("devsage.review", async () => {

      if (isRequestRunning) {
        vscode.window.showWarningMessage(
          "DevSage is already analyzing..."
        );
        return;
      }

      const editor = vscode.window.activeTextEditor;
      if (!editor) return;

      const document = editor.document;
      const code = document.getText();
      const language = document.languageId;

      const workspaceFolder =
        vscode.workspace.getWorkspaceFolder(document.uri);

      const projectPath = workspaceFolder?.uri.fsPath;

      const output =
        vscode.window.createOutputChannel("DevSage");

      output.clear();
      output.show(true);

      isRequestRunning = true;

      try {

        const result = await analyzeCode(
          code,
          language,
          "review",
          projectPath
        );

        latestResult = result || {};

        diagnosticCollection.clear();

        const diagnostics: vscode.Diagnostic[] = [];

        // =========================
        // BUGS
        // =========================

        (result?.bugs || []).forEach((bug: any) => {

          if (typeof bug.line !== "number") return;

          const lineIndex = bug.line - 1;

          if (
            lineIndex < 0 ||
            lineIndex >= document.lineCount
          ) return;

          const line =
            document.lineAt(lineIndex);

          const range = new vscode.Range(
            lineIndex,
            0,
            lineIndex,
            line.text.length
          );

          const diagnostic =
            new vscode.Diagnostic(
              range,
              bug.message || "Issue detected",
              vscode.DiagnosticSeverity.Warning
            );

          diagnostic.source = "DevSage";

          diagnostics.push(diagnostic);
        });

        // =========================
        // SECURITY
        // =========================

        (result?.security || []).forEach((issue: any) => {

          if (typeof issue.line !== "number") return;

          const lineIndex = issue.line - 1;

          if (
            lineIndex < 0 ||
            lineIndex >= document.lineCount
          ) return;

          const line =
            document.lineAt(lineIndex);

          const range = new vscode.Range(
            lineIndex,
            0,
            lineIndex,
            line.text.length
          );

          const diagnostic =
            new vscode.Diagnostic(
              range,
              issue.message || "Security issue",
              vscode.DiagnosticSeverity.Error
            );

          diagnostic.source = "DevSage Security";

          diagnostics.push(diagnostic);
        });

        diagnosticCollection.set(
          document.uri,
          diagnostics
        );

        // =========================
        // OUTPUT PANEL
        // =========================

        output.appendLine("══════════════════════════");
        output.appendLine("🔍 DevSage Code Review");
        output.appendLine("══════════════════════════\n");

        output.appendLine(`📊 Score: ${result?.score ?? 0}`);

        if (result?.risk_score !== undefined) {
          output.appendLine(`🛡 Risk Score: ${result.risk_score}`);
        }

        output.appendLine(
          `\n⏱ Time Complexity: ${result?.time_complexity ?? "N/A"}`
        );

        output.appendLine(
          `💾 Space Complexity: ${result?.space_complexity ?? "N/A"}`
        );

        if (!(result?.bugs?.length)) {
          output.appendLine("\nNo bugs detected.");
        }

        if (!(result?.security?.length)) {
          output.appendLine("\nNo security issues found.");
        }

        if (result?.emotional_feedback) {
          output.appendLine("\n💡 Emotional Feedback:");
          output.appendLine(result.emotional_feedback);
        }

      }
      catch {

        vscode.window.showErrorMessage(
          "DevSage review failed."
        );

      }
      finally {

        isRequestRunning = false;

      }

    })
  );

  // =========================================================
  // WORKSPACE SCAN
  // =========================================================

  context.subscriptions.push(
    vscode.commands.registerCommand(
      "devsage.scanWorkspace",
      async () => {

        const output =
          vscode.window.createOutputChannel(
            "DevSage Security"
          );

        output.clear();
        output.show(true);

        let files =
          await vscode.workspace.findFiles(
            "**/*.{py,js,ts,java,cpp,cs}",
            "**/node_modules/**"
          );

        if (files.length > 50) {

          vscode.window.showWarningMessage(
            "Large workspace detected. Scanning first 50 files only."
          );

          files = files.slice(0, 50);
        }

        let totalIssues: any[] = [];

        for (const file of files) {

          try {

            const document =
              await vscode.workspace.openTextDocument(file);

            const result =
              await analyzeCode(
                document.getText(),
                document.languageId,
                "workspace"
              );

            const security =
              result?.security || [];

            if (security.length > 0) {

              output.appendLine(`\n📂 ${file.fsPath}`);

              security.forEach((issue: any) => {

                output.appendLine(
                  `[${issue?.severity ?? "UNKNOWN"}] ${issue?.message ?? "Issue"}`
                );

              });

              totalIssues.push(...security);
            }

          }
          catch {
            continue;
          }
        }

        if (totalIssues.length === 0) {

          output.appendLine(
            "\n✅ No security vulnerabilities found."
          );

        } else {

          output.appendLine(
            `\n🚨 Total Issues: ${totalIssues.length}`
          );

        }

        latestResult = {
          ...(latestResult || {}),
          security: totalIssues
        };
      }
    )
  );

  // =========================================================
  // APPLY ALL FIXES
  // =========================================================

  context.subscriptions.push(
    vscode.commands.registerCommand(
      "devsage.applyAllFixes",
      async () => {

        if (isRequestRunning) {
          vscode.window.showWarningMessage(
            "DevSage is already applying a fix..."
          );
          return;
        }

        const editor =
          vscode.window.activeTextEditor;

        if (!editor || !latestResult) {

          vscode.window.showInformationMessage(
            "No fixes available."
          );

          return;
        }

        const bugs =
          latestResult?.bugs || [];

        if (!bugs.length) {

          vscode.window.showInformationMessage(
            "No fixes available."
          );

          return;
        }

        const confirm =
          await vscode.window.showInformationMessage(
            "Apply AI fixes for all detected issues?",
            "Yes",
            "Cancel"
          );

        if (confirm !== "Yes") return;

        const document = editor.document;

        isRequestRunning = true;

        try {

          const aiFix =
            await requestAIFix(
              document.getText(),
              document.languageId,
              "Fix all detected issues"
            );

          if (!aiFix?.fixed_code) {
            vscode.window.showErrorMessage(
              "AI returned empty fix."
            );
            return;
          }

          const fullRange =
            new vscode.Range(
              0,
              0,
              document.lineCount,
              0
            );

          const edit =
            new vscode.WorkspaceEdit();

          edit.replace(
            document.uri,
            fullRange,
            aiFix.fixed_code
          );

          await vscode.workspace.applyEdit(edit);

          vscode.window.showInformationMessage(
            "DevSage applied AI fixes."
          );

          await vscode.commands.executeCommand(
            "devsage.review"
          );

        }
        finally {
          isRequestRunning = false;
        }
      }
    )
  );

  // =========================================================
  // APPLY SECURITY FIX
  // =========================================================

  context.subscriptions.push(
    vscode.commands.registerCommand(
      "devsage.applySecurityFix",
      async () => {

        if (isRequestRunning) return;

        const editor =
          vscode.window.activeTextEditor;

        if (!editor) return;

        const securityIssues =
          latestResult?.security || [];

        if (!securityIssues.length) {
          vscode.window.showInformationMessage(
            "No security issues to fix."
          );
          return;
        }

        type SecurityPickItem = vscode.QuickPickItem & {
          issue: any;
        };

        const items: SecurityPickItem[] = securityIssues.map((issue: any) => ({
          label: issue.message,
          description: issue.severity ? `[${issue.severity}]` : "",
          issue
        }));

        const picked = await vscode.window.showQuickPick(items);

        if (!picked) return;

        const aiFix =
          await requestAIFix(
          editor.document.getText(),
          editor.document.languageId,
          picked.issue.message
        );

        if (!picked) return;

        isRequestRunning = true;

        try {

          const aiFix =
            await requestAIFix(
              editor.document.getText(),
              editor.document.languageId,
              picked.issue.message
            );

          if (!aiFix?.fixed_code) return;

          const fullRange =
            new vscode.Range(
              0,
              0,
              editor.document.lineCount,
              0
            );

          const edit =
            new vscode.WorkspaceEdit();

          edit.replace(
            editor.document.uri,
            fullRange,
            aiFix.fixed_code
          );

          await vscode.workspace.applyEdit(edit);

          vscode.window.showInformationMessage(
            "Security fix applied."
          );

        }
        finally {
          isRequestRunning = false;
        }
      }
    )
  );

  // =========================================================
  // PIN DEPENDENCY
  // =========================================================

  context.subscriptions.push(
    vscode.commands.registerCommand(
      "devsage.pinDependency",
      async () => {

        const editor =
          vscode.window.activeTextEditor;

        if (!editor) {
          vscode.window.showErrorMessage(
            "Open a file first."
          );
          return;
        }

        const document = editor.document;
        const position = editor.selection.active;

        const line =
          document.lineAt(position.line).text;

        const match =
          line.match(/"([^"]+)":\s*"\^?~?(\d+\.\d+\.\d+)"/) ||
          line.match(/([\w\-]+)==(\d+\.\d+\.\d+)/) ||
          line.match(/([\w\-]+)@(\^?\d+\.\d+\.\d+)/);

        if (!match) {

          vscode.window.showInformationMessage(
            "No dependency detected."
          );

          return;
        }

        const version = match[2];
        const pinned = version.replace(/[\^~]/g, "");

        const newLine =
          line.replace(version, pinned);

        const edit =
          new vscode.WorkspaceEdit();

        edit.replace(
          document.uri,
          document.lineAt(position.line).range,
          newLine
        );

        await vscode.workspace.applyEdit(edit);

        vscode.window.showInformationMessage(
          `Dependency pinned to ${pinned}`
        );
      }
    )
  );

}

export function deactivate() {}