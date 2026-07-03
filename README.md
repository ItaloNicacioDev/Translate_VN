# Translate VN

Ferramenta CLI para tradução de Visual Novels feitas em **Ren'Py**.  
CLI tool for translating **Ren'Py** Visual Novels.

---

## 🇧🇷 Português

### O que é

Translate VN é uma ferramenta de linha de comando que automatiza o processo de tradução de jogos feitos no engine Ren'Py. Ela extrai os diálogos do jogo, traduz automaticamente via Google Tradutor, permite revisão manual e gera um pacote de tradução pronto para aplicar no jogo.

### Requisitos

- Windows 10 ou superior
- Conexão com a internet (para a tradução automática)
- O executável `TranslateVN.exe` e os arquivos `config.json` e `database.db` devem estar **na mesma pasta**

### Estrutura de pastas esperada

```
📁 TranslateVN/
├── TranslateVN.exe
├── config.json
├── database.db
├── 📁 projects/
├── 📁 logs/
├── 📁 backups/
└── 📁 exports/
```

> As pastas `projects/`, `logs/`, `backups/` e `exports/` são criadas automaticamente na primeira execução caso não existam.

---

### Como usar

Execute o `TranslateVN.exe` e siga o menu interativo.

#### Fluxo completo de tradução

```
1. Novo Projeto   →  informe um nome e o caminho da pasta do jogo
2. Abrir Projeto  →  selecione o projeto criado
```

Dentro do projeto, siga as opções **na ordem**:

| Opção | O que faz |
|-------|-----------|
| **1 - Detectar jogo** | Identifica a versão do Ren'Py e lista os arquivos encontrados |
| **2 - Extrair arquivos** | Descompacta os `.rpa` e copia os scripts `.rpy` para a pasta temporária do projeto |
| **3 - Ler diálogos (indexar)** | Lê todos os scripts e salva os diálogos no banco de dados |
| **4 - Traduzir automaticamente** | Envia os diálogos para o Google Tradutor em paralelo e salva o resultado |
| **5 - Revisar / editar diálogos** | Permite ver e corrigir as traduções manualmente antes de gerar o pacote |
| **6 - Gerar pacote de tradução** | Compila os arquivos `.rpy` traduzidos na pasta `exports/` do projeto |
| **7 - Aplicar tradução** | Copia os arquivos gerados para dentro da pasta do jogo (com opção de backup) |
| **8 - Remover tradução aplicada** | Remove os arquivos de tradução do jogo |

---

### Menu de revisão (opção 5)

- Digite o **ID** de um diálogo para editar a tradução manualmente
- `n` — próxima página
- `p` — página anterior
- `r<ID>` — restaura o diálogo ao texto original (ex: `r42`)
- `d<ID>` — exclui a tradução da linha (ex: `d42`)
- `0` — voltar

---

### Configurações (opção 5 do menu principal)

| Chave | Descrição |
|-------|-----------|
| `language` | Idioma da interface (`pt_BR`, `en`) |
| `projects_folder` | Pasta onde os projetos são salvos |
| `auto_backup` | Criar backup automático antes de aplicar tradução (`true`/`false`) |
| `log_level` | Nível de log (`INFO`, `DEBUG`, `WARNING`) |
| `unrpyc_path` | Caminho manual para o script `unrpyc.py` (opcional) |

---

### Observações

- A tradução automática usa o **Google Tradutor gratuito** via internet. Jogos com muitos diálogos podem demorar alguns minutos.
- Linhas com tags Ren'Py (`{b}`, `{size=...}`, `[nome]`) são protegidas durante a tradução para não quebrarem o jogo.
- O backup feito pela opção 7 cria um `.zip` com apenas os arquivos que serão substituídos — não compacta os assets do jogo inteiro.
- Arquivos `.rpyc` compilados são descompilados automaticamente usando o [unrpyc](https://github.com/CensoredUsername/unrpyc), baixado na primeira vez que for necessário.

---
---

## 🇺🇸 English

### What is it

Translate VN is a command-line tool that automates the translation process for games made with the Ren'Py engine. It extracts dialogues from the game, automatically translates them via Google Translate, allows manual review, and generates a translation package ready to apply to the game.

### Requirements

- Windows 10 or later
- Internet connection (for automatic translation)
- The executable `TranslateVN.exe` and the files `config.json` and `database.db` must be **in the same folder**

### Expected folder structure

```
📁 TranslateVN/
├── TranslateVN.exe
├── config.json
├── database.db
├── 📁 projects/
├── 📁 logs/
├── 📁 backups/
└── 📁 exports/
```

> The `projects/`, `logs/`, `backups/` and `exports/` folders are created automatically on first run if they don't exist.

---

### How to use

Run `TranslateVN.exe` and follow the interactive menu.

#### Full translation workflow

```
1. New Project  →  enter a name and the path to the game folder
2. Open Project →  select the project you created
```

Inside a project, follow the options **in order**:

| Option | What it does |
|--------|-------------|
| **1 - Detect game** | Identifies the Ren'Py version and lists found files |
| **2 - Extract files** | Unpacks `.rpa` archives and copies `.rpy` scripts to the project's temp folder |
| **3 - Read dialogues (index)** | Reads all scripts and saves the dialogues to the database |
| **4 - Auto translate** | Sends dialogues to Google Translate in parallel and saves the results |
| **5 - Review / edit dialogues** | Lets you view and manually correct translations before generating the package |
| **6 - Generate translation package** | Compiles the translated `.rpy` files into the project's `exports/` folder |
| **7 - Apply translation** | Copies the generated files into the game folder (with optional backup) |
| **8 - Remove applied translation** | Removes translation files from the game |

---

### Review menu (option 5)

- Type a dialogue **ID** to manually edit its translation
- `n` — next page
- `p` — previous page
- `r<ID>` — restore dialogue to original text (e.g. `r42`)
- `d<ID>` — delete the translation for that line (e.g. `d42`)
- `0` — go back

---

### Settings (option 5 from main menu)

| Key | Description |
|-----|-------------|
| `language` | Interface language (`pt_BR`, `en`) |
| `projects_folder` | Folder where projects are saved |
| `auto_backup` | Auto-create backup before applying translation (`true`/`false`) |
| `log_level` | Log level (`INFO`, `DEBUG`, `WARNING`) |
| `unrpyc_path` | Manual path to the `unrpyc.py` script (optional) |

---

### Notes

- Automatic translation uses the **free Google Translate** API over the internet. Games with many dialogues may take a few minutes.
- Lines containing Ren'Py tags (`{b}`, `{size=...}`, `[name]`) are protected during translation to prevent breaking the game.
- The backup created by option 7 only zips the files that will be overwritten — it does not compress the entire game assets folder.
- Compiled `.rpyc` files are automatically decompiled using [unrpyc](https://github.com/CensoredUsername/unrpyc), downloaded the first time it is needed.

---

## License

MIT