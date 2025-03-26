# Real-Time Chat App

Este projeto é uma aplicação de chat em tempo real desenvolvida com o Flet, que permite falar em salas de chat e privada entre utilizadores. Além das funcionalidades básicas, foram implementadas funcionalidades extra para melhorar a experiência do utilizador e a segurança da aplicação.

---

## Funcionalidades Extra

### 1. **Menssagens Privadas**
A funcionalidade de menssagens privadas foi incluída para permitir que os utilizadores comuniquem de forma mais pessoal e segura, sem que as suas mensagens sejam visíveis em salas públicas. Esta funcionalidade é essencial para situações em que os utilizadores precisam de discutir assuntos sensíveis ou manter conversas individuais.

**Descrição Detalhada:**  
- Os utilizadores podem iniciar um chat privado clicando no nome de outro utilizador na lista de utilizadores registados.  
- As mensagens privadas são armazenadas com um prefixo único no armazenamento local, garantindo que só os participantes da conversa tenham acesso.  
- A interface exibe um cabeçalho indicando o destinatário e inclui um botão para voltar ao chat público.  
- As mensagens privadas têm um estilo visual distinto (cor roxa) para diferenciá-las das mensagens públicas.  

**Instruções de Utilização:**  
1. Navegue para a lista de utilizadores clicando no ícone "People" no canto superior direito.  
2. Clique no nome do utilizador com quem deseja conversar.  
3. Troque mensagens privadas.  
4. Para voltar ao chat público, clique no botão "Back to Public Chat".  

---

### 2. **Edição e Limpeza de Mensagens**
A possibilidade de editar mensagens foi adicionada para permitir que os utilizadores corrijam erros ou atualizem o conteúdo das suas mensagens após o envio. A funcionalidade de limpeza de mensagens permite aos utilizadores remover todo o histórico de uma sala, útil para manter a privacidade ou reiniciar conversas.

**Descrição Detalhada:**  
- As mensagens enviadas pelo utilizador atual têm um botão de edição. Ao clicar, é exibido um campo de texto para edição e um botão para salvar as alterações.  
- A mensagem editada é atualizada no armazenamento local e refletida em tempo real para todos os participantes.  
- O botão "Clear Chat" remove todas as mensagens da sala atual, seja pública ou privada.  

**Instruções de Utilização:**  
1. Para editar uma mensagem:  
   - Clique no ícone de edição (lápis) ao lado da mensagem.  
   - Edite o texto no campo exibido.  
   - Clique no ícone de salvar (disquete) para confirmar.  
2. Para limpar o chat:  
   - Clique no botão "Clear Chat" na parte inferior da interface.  

---

### 3. **Sistema de Notificações e Atualização em Tempo Real**
**Motivo de Inclusão:**  
Esta funcionalidade foi implementada para garantir que todos os utilizadores recebam atualizações imediatas sobre novas mensagens, edições ou ações de outros utilizadores, melhorando a experiência de chat em tempo real.

**Descrição Detalhada:**  
- O sistema utiliza o mecanismo `pubsub` do Flet para enviar e receber atualizações em tempo real.  
- Mensagens de sistema (ex.: "Utilizador X entrou na sala") são exibidas em estilo diferenciado (itálico e cinzento).  
- A lista de utilizadores e salas de chat é atualizada dinamicamente sem necessidade de recarregar a página.  

**Instruções de Utilização:**  
- As atualizações são automáticas. Basta estar conectado à sala ou chat privado para ver as mudanças.  

---

## Como Executar o Projeto
1. Certifique-se de ter Python instalado.  
2. Instale as dependências: `pip install flet`.  
3. Execute o ficheiro `main.py`: `python main.py`.  
4. A aplicação abrirá no navegador padrão no endereço `http://localhost:2020`.  

---

**Nota:** Este projeto utiliza armazenamento local do navegador, pelo que os dados persistem apenas durante a sessão atual. Para uma solução permanente, seria necessário integrar uma base de dados.
