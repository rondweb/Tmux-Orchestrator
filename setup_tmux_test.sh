#!/bin/bash

# Nome da sessão e janela
SESSION="session"
WINDOW="window"

# Cria a sessão tmux em background se não existir
tmux has-session -t $SESSION 2>/dev/null
if [ $? != 0 ]; then
  tmux new-session -d -s $SESSION -n $WINDOW
  echo "Sessão '$SESSION' e janela '$WINDOW' criadas."
else
  # Cria a janela se não existir
  tmux list-windows -t $SESSION | grep -q $WINDOW
  if [ $? != 0 ]; then
    tmux new-window -t $SESSION -n $WINDOW
    echo "Janela '$WINDOW' criada na sessão '$SESSION'."
  else
    echo "Sessão '$SESSION' e janela '$WINDOW' já existem."
  fi
fi

# Anexa à sessão tmux
echo "Anexando à sessão tmux. Use Ctrl+b d para sair."
tmux attach-session -t $SESSION