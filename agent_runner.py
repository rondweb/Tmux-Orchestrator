import os
import re
from llm_handler import LLMHandler

def extract_project_name(context):
    # Procura o primeiro heading de nível 1 (ex: # NomeDoProjeto)
    match = re.search(r"^# (.+)", context, re.MULTILINE)
    if match:
        return match.group(1).strip().replace(" ", "_").lower() + "_output"
    return "output_project"

def save_files_from_llm_response(response, output_dir):
    # Procura blocos do tipo ```filename\next\nconteudo\n```
    file_blocks = re.findall(r"```([\w\-.\/]+)\n([\s\S]*?)```", response)
    if not file_blocks:
        # fallback: procura por blocos markdown com nome do arquivo no texto
        file_blocks = re.findall(r"#\s*([\w\-.\/]+)\n([\s\S]*?)(?=\n#|$)", response)
    for filename, content in file_blocks:
        filepath = os.path.join(output_dir, filename.strip())
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            f.write(content.strip())
        print(f"Arquivo criado: {filepath}")

def main():
    handler = LLMHandler()
    print("Agente LLM pronto! Digite o nome do arquivo de contexto markdown ou pressione Ctrl+C para sair.")
    while True:
        try:
            context_file = input("Arquivo de contexto (.md): ")
            with open(context_file, "r") as f:
                context = f.read()
            project_dir = extract_project_name(context)
            os.makedirs(project_dir, exist_ok=True)
            prompt = f"Com base neste contexto de projeto:\n{context}\nCrie todos os arquivos necessários para iniciar o projeto, incluindo README.md, estrutura de pastas e arquivos de exemplo. Use blocos markdown do tipo ```caminho/arquivo.ext\nconteudo\n``` para cada arquivo."
            response = handler.send_message("agent", prompt)
            print("\nResposta do LLM:\n", response)
            save_files_from_llm_response(response, project_dir)
        except KeyboardInterrupt:
            print("\nAgente encerrado.")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    main()
