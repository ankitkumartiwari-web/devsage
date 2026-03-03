import * as vscode from "vscode";
import { analyzeCode, requestAIFix } from "./api";

let diagnosticCollection: vscode.DiagnosticCollection;
let latestResult: any = null;

export function activate(context: vscode.ExtensionContext) {
  diagnosticCollection =
    vscode.languages.createDiagnosticCollection("devsage");

  context.subscriptions.push(diagnosticCollection);

  // =========================================================
  // REVIEW COMMAND (AI MODE)
  // =========================================================

  context.subscriptions.push(
    vscode.commands.registerCommand("devsage.review", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;

      const document = editor.document;
      const code = document.getText();
      const language = document.languageId;

      const workspaceFolder =
        vscode.workspace.getWorkspaceFolder(document.uri);
      const projectPath = workspaceFolder?.uri.fsPath;

      const output = vscode.window.createOutputChannel("DevSage");
      output.clear();
      output.show(true);

      try {
        const result = await analyzeCode(
          code,
          language,
          "review",
          projectPath
        );

        latestResult = result;
        diagnosticCollection.clear();

        const diagnostics: vscode.Diagnostic[] = [];

        (result.bugs || []).forEach((bug: any) => {
          if (typeof bug.line === "number") {
            const lineIndex = bug.line - 1;
            if (lineIndex >= 0 && lineIndex < document.lineCount) {
              const line = document.lineAt(lineIndex);
              const range = new vscode.Range(
                lineIndex,
                0,
                lineIndex,
                line.text.length
              );

              const diagnostic = new vscode.Diagnostic(
                range,
                bug.message,
                vscode.DiagnosticSeverity.Warning
              );

              diagnostic.source = "DevSage";
              diagnostics.push(diagnostic);
            }
          }
        });

        diagnosticCollection.set(document.uri, diagnostics);

        // OUTPUT PANEL
        output.appendLine("══════════════════════════");
        output.appendLine("🔍 DevSage Code Review");
        output.appendLine("══════════════════════════\n");

        output.appendLine(`📊 Score: ${result.score ?? 0}`);
        if (result.risk_score !== undefined) {
          output.appendLine(`🛡 Risk Score: ${result.risk_score}`);
        }

        output.appendLine(`\n⏱ Time Complexity: ${result.time_complexity}`);
        output.appendLine(`💾 Space Complexity: ${result.space_complexity}`);

        if ((result.bugs || []).length === 0) {
          output.appendLine("\nNo bugs detected.");
        }

        if ((result.security || []).length === 0) {
          output.appendLine("\nNo security issues found.");
        }

        if (result.emotional_feedback) {
          output.appendLine("\n💡 Emotional Feedback:");
          output.appendLine(result.emotional_feedback);
        }
      } catch (error) {
        vscode.window.showErrorMessage("DevSage failed.");
      }
    })
  );

  // =========================================================
  // WORKSPACE SCAN (STATIC ONLY)
  // =========================================================

  context.subscriptions.push(
    vscode.commands.registerCommand("devsage.scanWorkspace", async () => {
      const output = vscode.window.createOutputChannel(
        "DevSage Security"
      );
      output.clear();
      output.show(true);

      const files = await vscode.workspace.findFiles(
        "**/*.{py,js,ts,java,cpp,cs}",
        "**/node_modules/**"
      );

      let totalIssues: any[] = [];

      for (const file of files) {
        try {
          const document =
            await vscode.workspace.openTextDocument(file);

          const result = await analyzeCode(
            document.getText(),
            document.languageId,
            "workspace"
          );

          const security = result.security || [];

          if (security.length > 0) {
            output.appendLine(`\n📂 ${file.fsPath}`);
            security.forEach((issue: any) => {
              output.appendLine(
                `[${issue.severity}] ${issue.message}`
              );
            });

            totalIssues.push(...security);
          }
        } catch {
          continue;
        }
      }

      if (totalIssues.length === 0) {
        output.appendLine("\n✅ No security vulnerabilities found.");
      } else {
        output.appendLine(`\n🚨 Total Issues: ${totalIssues.length}`);
      }

      latestResult = {
        ...(latestResult || {}),
        security: totalIssues,
      };
    })
  );

  // =========================================================
  // APPLY ALL FIXES (AI FIX MODE)
  // =========================================================

  context.subscriptions.push(
    vscode.commands.registerCommand("devsage.applyAllFixes", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || !latestResult) {
        vscode.window.showInformationMessage(
          "No fixes available."
        );
        return;
      }

      const document = editor.document;
      const bugs = latestResult.bugs || [];

      if (bugs.length === 0) {
        vscode.window.showInformationMessage(
          "No fixes available."
        );
        return;
      }

      const confirm = await vscode.window.showInformationMessage(
        "Apply AI fixes for all detected issues?",
        "Yes",
        "Cancel"
      );

      if (confirm !== "Yes") return;

      try {
        const aiFix = await requestAIFix(
          document.getText(),
          document.languageId,
          "Fix all detected issues"
        );

        if (!aiFix.fixed_code) {
          vscode.window.showErrorMessage(
            "AI returned empty fix."
          );
          return;
        }

        const fullRange = new vscode.Range(
          0,
          0,
          document.lineCount,
          0
        );

        const edit = new vscode.WorkspaceEdit();
        edit.replace(document.uri, fullRange, aiFix.fixed_code);

        await vscode.workspace.applyEdit(edit);

        vscode.window.showInformationMessage(
          "DevSage applied AI fixes."
        );

        await vscode.commands.executeCommand("devsage.review");
      } catch {
        vscode.window.showErrorMessage(
          "AI fix failed."
        );
      }
    })
  );

  // =========================================================
  // EXPORT SECURITY REPORT
  // =========================================================

  context.subscriptions.push(
    vscode.commands.registerCommand(
      "devsage.exportSecurityReport",
      async () => {
        if (!latestResult?.security?.length) {
          vscode.window.showInformationMessage(
            "No security data to export."
          );
          return;
        }

        const uri = await vscode.window.showSaveDialog({
          filters: { JSON: ["json"] },
        });

        if (!uri) return;

        await vscode.workspace.fs.writeFile(
          uri,
          Buffer.from(
            JSON.stringify(latestResult.security, null, 2)
          )
        );

        vscode.window.showInformationMessage(
          "Security report exported."
        );
      }
    )
  );
}

export function deactivate() {}