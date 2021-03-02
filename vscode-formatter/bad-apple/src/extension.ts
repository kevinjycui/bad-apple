// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as frames from './data.json';

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "bad-apple" is now active!');

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with registerCommand
	// The commandId parameter must match the command field in package.json
	let disposable = vscode.commands.registerCommand('bad-apple.helloWorld', () => {
		// The code you place here will be executed every time your command is executed

		// Display a message box to the user
		vscode.window.showInformationMessage('Hello World from Bad Apple!!');
	});

	let index = 0;

	const maxFrame = 4382;
	const buffer = 3;
	let bufferi = 3;

	let formatter = vscode.commands.registerCommand('bad-apple.format', () => {

		const { activeTextEditor } = vscode.window;

		if (index >= maxFrame) {
			return;
		}

		else if (index == 0) {
			vscode.window.showInformationMessage('【東方】Bad Apple!! ＰＶ【影絵】 brought to you by Junferno!');
		}

		if (bufferi < buffer) {
			bufferi++;
			return;
		}

		bufferi = 0;

		if (activeTextEditor) {
			const { document } = activeTextEditor;

			let tokens = ''

			for (let ln=0; ln<document.lineCount; ln++) {
				let lnTokens = document.lineAt(ln).text.replace('/\s+/g', ' ').split(' ');
				for (let cn=0; cn<lnTokens.length; cn++)
						tokens += lnTokens[cn]
			}

			const width = 36;
			const height = 28;

			let txtIndex = 0;
			let newText = '';

			for (let x=0; x<height; x++) {
				for (let y=0; y<width; y++) {
					if (frames[index][x][y] === 0) {
						newText += tokens[txtIndex] + tokens[txtIndex+1] + tokens[txtIndex+2];
						txtIndex+=3;
					}
					else {
						newText += '   ';
					}
				}
				newText += '\n';
			}

			for (; txtIndex < tokens.length; txtIndex++)
				if (tokens[txtIndex].length > 0)
					newText += tokens[txtIndex];
			
			const edit = new vscode.WorkspaceEdit();
			edit.replace(document.uri, new vscode.Range(document.lineAt(0).range.start, document.lineAt(document.lineCount - 1).range.end), newText + '\n');
			
			index++;

			vscode.workspace.applyEdit(edit);
			document.save();

		}
	
	});

	context.subscriptions.push(disposable);
	context.subscriptions.push(formatter);
	
}

// this method is called when your extension is deactivated
export function deactivate() {}
