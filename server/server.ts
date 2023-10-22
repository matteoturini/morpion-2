const games = new Map<string, [WebSocket, WebSocket?]>();
const rGames = new Map<WebSocket, string>();

const codeCharacters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";

function randomInt(min: number, max: number) {
    return Math.floor((Math.random() * (max-min+1)));
}

function generateCode(): string {
    let code = "";
    for (let i = 0; i < 6; i++) {
        code += codeCharacters[randomInt(0, codeCharacters.length - 1)];
    }
    return code;
}

function gameLoop(code: string) {
    const players = games.get(code)!;
    const player1 = players[0];
    const player2 = players[1];
    if (player2 === undefined) {
        throw new TypeError("Invalid player2 type.");
    }
    player1.addEventListener("message", ({ data }) => {
        console.log({player1: data})
        if (data == "quit") {
            player2.send("quit");
            player2.close();
        }
        player2.send(data);
    });
    player2.addEventListener("message", ({ data }) => {
        console.log({player2: data})
        if (data == "quit") {
            player1.send("quit");
            player1.close();
        }
        player1.send(data);
    });
}

// deno-lint-ignore no-explicit-any
function ignoreErrors(func: (...anything: any[]) => any) {
    // deno-lint-ignore no-explicit-any
    function wrapped(...args: any[]) {
        try {
            return func(...args);
        } catch(e) {
            console.error(e);
        }
    }
    return wrapped;
}

Deno.serve({
    handler: (request) => {
      const {
        response,
        socket,
      } = Deno.upgradeWebSocket(request);
      socket.addEventListener("message", ignoreErrors((event) => {
        if (typeof event.data !== "string") {
            socket.send('error')
            socket.close()
            return;
        }
        console.log(event.data);
        if (event.data == "create") {
            console.log("creating game...")
            // create
            let code = generateCode();
            while (true) {
                let foundCode = false;
                for (const existing of games.keys()) {
                    if (existing == code) {
                        console.log("code found")
                        code = generateCode();
                        foundCode = true;
                        break;
                    }
                }
                if (!foundCode) {
                    foundCode = false;
                    break;
                }
            }

            console.log("loopexit");
            games.set(code, [socket, undefined]);
            rGames.set(socket, code);
            socket.addEventListener("close", (_ev) => {
                console.log("socket closed");
                if (games.has(code) && games.get(code)![1]) {
                    const player2 = games.get(code)![1]!;
                    if (player2.readyState == WebSocket.OPEN) {
                        player2.send("disconnected");
                        player2.close();

                    }
                    games.delete(code);
                }
                rGames.delete(socket);
            });
            socket.send(code);
        } else if (event.data.match(/[A-Z0-9]{5}/)) {
            // join
            if (games.has(event.data)) {
                const player1 = games.get(event.data)![0];
                const player2 = socket;
                games.set(event.data, [player1, player2]);
                player1.send("joined");
                player2.send("joined");
                gameLoop(event.data);
            }
        }
      }));
      return response;
    },
});