compare esse css com o html utilizado junto com ele com o meu atual







homeLyfesync.css antigo





:root {



    --azul-automaster-escuro: #111111;



    --vermelho-automaster: #e73f4e;



    --cinza-claro: #f5f5f5;



    --linha-separacao: #e0e0e0;



    --texto-escuro: #333;



}







/\* Estilos globais e reset \*/



body {



    margin: 0;



    font-family: Arial, sans-serif;



    line-height: 1.6;



    color: var(--texto-escuro);



}







a {



    text-decoration: none;



    color: inherit;



    transition: color 0.3s ease;



}







ul {



    list-style: none;



    padding: 0;



    margin: 0;



}







/\* -------------------- CABEÇALHO -------------------- \*/



.automaster-header {



    background-color: white;



    padding: 20px 0;



}







.header-container {



    max-width: 1200px;



    margin: 0 auto;



    display: flex;



    justify-content: space-between;



    align-items: center;



}







.logo-container {



    display: flex;



    align-items: center;



    column-gap: 15px;



}







.logo-img {



    height: 110px;



}







.logo-text {



    font-size: 24px;



    font-weight: bold;



    color: var(--azul-automaster-escuro);



}







.main-nav ul {



    display: flex;



    column-gap: 30px;



    align-items: center;



}







.nav-link {



    font-weight: bold;



    text-transform: uppercase;



    padding: 10px 0;



    border-bottom: 2px solid transparent;



    transition: border-color 0.3s ease;



}







.nav-link:hover, .nav-active {



    color: var(--vermelho-automaster);



    border-bottom-color: var(--vermelho-automaster);



}







.nav-button {



    padding: 8px 15px;



    border: 1px solid var(--texto-escuro);



    border-radius: 5px;



    color: var(--texto-escuro);



    transition: background-color 0.3s ease, color 0.3s ease;



}







.nav-button:hover {



    background-color: var(--vermelho-automaster);



    color: white;



    border-color: var(--vermelho-automaster);



}







/\* -------------------- CORPO DA PÁGINA -------------------- \*/



.main-content {



    background-color: var(--cinza-claro);



    padding: 40px;



    min-height: 400px;



}







/\* Estilos globais da masterpage \*/



.app-container {



    display: flex;



    flex-direction: column;



    min-height: 100vh;



}







.main-header {



    padding: 1rem 2rem;



}







.main-content {



    flex: 1;



    padding: 2rem;



}







.main-footer {



    padding: 1rem;



    text-align: center;



    background-color: #f8f9fa;



}







/\* --- ESTILOS DA HOME --- \*/



/\* Container da página home (com a imagem de fundo) \*/



.home-container {



    position: relative;



    width: 100%;



    min-height: 80vh;



    display: flex;



    justify-content: center;



    align-items: center;



    text-align: center;



    overflow: hidden;



}







/\* Pseudo-elemento para a imagem de fundo desfocada \*/



.home-container::before {



    content: '';



    position: absolute;



    top: 0;



    left: 0;



    width: 100%;



    height: 100%;



    background-size: cover;



    background-position: center;



    background-repeat: no-repeat;



    filter: blur(2px);



    transform: scale(1.05);



    z-index: -1;



}







/\* Estilo para o conteúdo (títulos e parágrafos) \*/



.text-content {



    color:#ffffff;



    z-index: 1;



    padding: 2rem;



    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;



}







h1 {



    font-size: 3.5rem;



    font-weight: bold;



    margin-bottom: 1rem;



}







p {



    font-size: 1.75rem;



    font-weight: bold;



}







/\* Pseudo-elemento para a imagem de fundo desfocada \*/



.home-container::before {



  content: '';



  position: absolute;



  top: 0;



  left: 0;



  width: 100%;



  height: 100%;



  background-size: contain;



  background-position: center;



  background-repeat: no-repeat;



  filter: blur(2px) brightness(0.7); /\* Adiciona um filtro de brilho para escurecer a imagem \*/



  transform: scale(1.05);



  z-index: -1;



}







/\* Estilo para a página da Área do Funcionário \*/



.employee-area {



    background-color: #fffafa;



}







/\* Linha de separação \*/



.separator-line {



    height: 1px;



    background-color: var(--linha-separacao);



}







/\* -------------------- RODAPÉ CORRIGIDO -------------------- \*/



.automaster-footer {



    position: fixed;



    bottom: 0;



    width: 100%;



    background-color: white; /\* Alterado para branco \*/



    color: var(--texto-escuro);



    padding: 30px 0;



}







.footer-container {



    max-width: 1200px;



    margin: 0 auto;



    /\* CORREÇÃO AQUI: Garante o layout de 3 partes \*/



    display: flex;



    justify-content: space-between;



    align-items: center;



    flex-wrap: wrap;



}







.footer-left {



    /\* CORREÇÃO AQUI: Garante que logo e menu fiquem juntos \*/



    display: flex;



    align-items: center;



    column-gap: 40px;



}







.footer-nav ul {



    /\* CORREÇÃO AQUI: Garante que os itens do menu fiquem lado a lado \*/



    display: flex;



    column-gap: 20px;



}







.footer-nav a {



    color: var(--texto-escuro);



    opacity: 0.8;



}







.footer-nav a:hover {



    opacity: 1;



}







.footer-logo-img {



    height: 40px;



}







.copyright-text {



    font-size: 14px;



    opacity: 0.7;



}







/\* -------------------- ESTILOS PARA LOGIN E REGISTRO -------------------- \*/







/\* Container principal \*/



.login-container,



.registro-container {



    min-height: 100vh;



    background: linear-gradient(135deg, var(--azul-automaster-escuro) 0%, #2c3e50 100%);



    display: flex;



    align-items: center;



    justify-content: center;



    padding: 20px;



}







/\* Card de login/registro \*/



.login-card,



.registro-card {



    background: white;



    border-radius: 20px;



    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);



    padding: 40px;



    width: 100%;



    max-width: 500px;



    text-align: center;



}







/\* Header do card \*/



.login-header,



.registro-header {



    margin-bottom: 30px;



}







.login-logo,



.registro-logo {



    height: 80px;



    margin-bottom: 20px;



}







.login-header h1,



.registro-header h1 {



    color: var(--azul-automaster-escuro);



    font-size: 2rem;



    margin-bottom: 10px;



    font-weight: bold;



}







.login-header p,



.registro-header p {



    color: #666;



    font-size: 1rem;



    margin: 0;



}







/\* Formulário \*/



.login-form,



.registro-form {



    margin-bottom: 30px;



}







.form-group {



    margin-bottom: 20px;



    text-align: left;



}







.form-row {



    display: grid;



    grid-template-columns: 1fr 1fr;



    gap: 20px;



}







.form-group label {



    display: block;



    margin-bottom: 8px;



    color: var(--azul-automaster-escuro);



    font-weight: bold;



    font-size: 0.9rem;



}







.form-group input {



    width: 100%;



    padding: 15px;



    border: 2px solid #e0e0e0;



    border-radius: 10px;



    font-size: 1rem;



    transition: border-color 0.3s ease, box-shadow 0.3s ease;



    box-sizing: border-box;



}







.form-group input:focus {



    outline: none;



    border-color: var(--vermelho-automaster);



    box-shadow: 0 0 0 3px rgba(231, 63, 78, 0.1);



}







/\* Botões \*/



.login-button,



.registro-button {



    width: 100%;



    padding: 15px;



    background: var(--vermelho-automaster);



    color: white;



    border: none;



    border-radius: 10px;



    font-size: 1.1rem;



    font-weight: bold;



    cursor: pointer;



    transition: background-color 0.3s ease, transform 0.2s ease;



    margin-top: 10px;



}







.login-button:hover,



.registro-button:hover {



    background: #d6333f;



    transform: translateY(-2px);



}







.login-button:disabled,



.registro-button:disabled {



    background: #ccc;



    cursor: not-allowed;



    transform: none;



}







/\* Mensagens de erro e sucesso \*/



.error-message {



    background: #fee;



    color: #c33;



    padding: 15px;



    border-radius: 10px;



    margin-bottom: 20px;



    border: 1px solid #fcc;



    font-size: 0.9rem;



}







.success-message {



    background: #efe;



    color: #363;



    padding: 15px;



    border-radius: 10px;



    margin-bottom: 20px;



    border: 1px solid #cfc;



    font-size: 0.9rem;



}







/\* Footer do card \*/



.login-footer,



.registro-footer {



    text-align: center;



}







.login-footer p,



.registro-footer p {



    margin-bottom: 15px;



    color: #666;



}







.link-registro,



.link-login {



    color: var(--vermelho-automaster);



    font-weight: bold;



    text-decoration: none;



}







.link-registro:hover,



.link-login:hover {



    text-decoration: underline;



}







.link-voltar {



    color: var(--azul-automaster-escuro);



    text-decoration: none;



    font-weight: bold;



    display: inline-block;



    margin-top: 10px;



    padding: 10px 20px;



    border: 2px solid var(--azul-automaster-escuro);



    border-radius: 8px;



    transition: all 0.3s ease;



}







.link-voltar:hover {



    background: var(--azul-automaster-escuro);



    color: white;



}







/\* Responsividade \*/



@media (max-width: 768px) {



    .login-card,



    .registro-card {



        padding: 30px 20px;



        margin: 20px;



    }



 



    .form-row {



        grid-template-columns: 1fr;



        gap: 0;



    }



 



    .login-header h1,



    .registro-header h1 {



        font-size: 1.5rem;



    }



}







registrarHumor.html antigo



{% extends 'app\_LyfeSync/layouts/masterpage\_logado.html' %}



{% load static %}



{% load custom\_filters %}



{% load app\_LyfeSync\_extras %}







{% block title %}



  Alterar Gratidão



{% endblock %}







{% block content\_logado %}



  <style>



    /\* Estilos Customizados Adicionais (Se o Tailwind não for suficiente) \*/



    .humor-image {



      width: 30px;



      /\* Tamanho da imagem, conforme solicitado \*/



      height: 30px;



      transition: transform 0.1s;



    }



 



    /\* Estilo para o container de humor selecionado \*/



    .selected-humor {



      background-color: #ecfdf5;



      /\* Tailwind: bg-green-50, um verde claro \*/



      border: 2px solid #34d399;



      /\* Tailwind: border-green-400 \*/



      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);



      transform: scale(1.05);



    }



 



    /\* Estilo para a textarea, baseado na sua imagem de referência \*/



    .custom-textarea {



      background-color: #e6f7ff;



      /\* Cor azul claro da imagem de anexo \*/



      border-radius: 20px;



      /\* Borda arredondada \*/



      border-color: #b3e0ff;



      /\* Cor da borda \*/



    }



 



    /\* Estilo do botão SALVAR \*/



    .btn-salvar-humor {



      background-color: #f44336;



      /\* Cor Laranja/Vermelho da imagem de anexo \*/



    }



 



    .btn-salvar-humor:hover {



      background-color: #d32f2f;



    }



 



    /\* Estilo para as imagens pequenas na tabela de humor \*/



    .humor-image-small {



      width: 20px;



      height: 20px;



    }



  </style>







  <div class="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">



    <div class="flex flex-wrap lg:flex-nowrap gap-8">



      <div class="w-full lg:w-3/5 bg-white p-6 rounded-xl shadow-lg">



        <h1 class="text-3xl font-bold text-lyfesync-green mb-8">Como você está se sentindo hoje?</h1>







        <form id="form-registro-humor" method="POST" action="{% url 'registrarHumor' %}">



          {% csrf\_token %}







          <div class="mb-6">



            <label for="id\\\_data" class="block text-xl font-semibold text-gray-700 mb-2">Data:</label>







            <input type="date" id="id\\\_data" name="data" class="w-full sm:w-1/2 p-3 border-2 border-green-200 rounded-lg focus:border-lyfesync-green focus:ring focus:ring-green-100 transition duration-150" value="{{ form.data.value|default\\\_if\\\_none:'' }}" required />







            {% if form.data.errors %}



              <div class="text-red-500 text-sm mt-1">{{ form.data.errors }}</div>



            {% endif %}



          </div>







          <div class="mb-10">



            <label class="block text-xl font-semibold text-gray-700 mb-4">Selecione seu Humor:</label>







            {# Oculta o widget completo do Django, mas ele deve existir para a validação #}



            <div id="hidden-radio-widget" style="display: none; visibility: hidden;">{{ form.estado }}</div>







            <div class="flex flex-wrap gap-4">



              {% for value, label in form.estado.field.choices %}



                {# O value agora é 'FELIZ', 'CALMO', etc. #}



                {% with image\_path=humor\_icon\_class\_map|get\_item:value|default:'img/icon/adchumor.png' %}



                  <div class="p-3 border-2 border-gray-100 rounded-xl cursor-pointer hover:shadow-md transition duration-150 flex flex-col items-center justify-center text-center" data-humor-container data-humor-value="{{ value }}" onclick="selectHumor('{{ value }}', this)">



                    {# O CAMINHO DA IMAGEM É OBTIDO PELO DICIONÁRIO #}



                    {% if value %}



                      <img src="{% static image\\\_path %}" alt="{{ label }}" class="humor-image" />



                    {% else %}



                      {# Se for o valor vazio (''), use a imagem padrão de placeholder #}



                      <img src="{% static 'img/icon/adchumor.png' %}" alt="{{ label }}" class="humor-image" />



                    {% endif %}







                    <span class="text-base font-semibold text-gray-700 pr-2">{{ label|split\_by\_space|first }}</span>



                  </div>



                {% endwith %}



              {% endfor %}



            </div>







            {% if form.estado.errors %}



              <div class="text-red-500 text-sm mt-1">{{ form.estado.errors }}</div>



            {% endif %}



          </div>







          <div class="mb-8">



            <label for="id\\\_descricaohumor" class="block text-xl font-semibold text-gray-700 mb-2">Descrição:</label>







            <textarea id="id\\\_descricaohumor" name="descricaohumor" rows="8" placeholder="Descreva brevemente o que motivou seu humor hoje..." class="w-full p-4 border-2 border-green-200 rounded-xl focus:border-lyfesync-green focus:ring focus:ring-green-100 transition duration-150 custom-textarea">{{ form.descricaohumor.value|default\_if\_none:'' }}</textarea>







            {% if form.descricaohumor.errors %}



              <div class="text-red-500 text-sm mt-1">{{ form.descricaohumor.errors }}</div>



            {% endif %}



          </div>







          <div class="flex justify-end">



            <button type="submit" class="btn-salvar-humor py-3 px-8 text-white font-bold rounded-xl shadow-lg transition duration-200">SALVAR</button>



          </div>



        </form>



      </div>







      <div class="w-full lg:w-2/5 space-y-8">



        <div class="bg-white p-6 rounded-xl shadow-lg border-t-4 border-lyfesync-green">



          <h2 class="text-2xl font-bold text-lyfesync-green mb-4">Tabela de Humor</h2>







          <div class="text-gray-700 space-y-4 text-sm">



            {# Ícones de referência no topo (Ajustado para 5 ícones em linha) #}







            <div class="flex justify-around items-center mb-6 border-b pb-4">



              {% for value, image\_path in humor\_icon\_class\_map.items %}



                <img src="{% static image\\\_path %}" alt="{{ value }}" class="humor-image-small" />



              {% endfor %}



            </div>







            {% for value, image\_path in humor\_icon\_class\_map.items %}



              <div class="flex items-start gap-3">



                <span class="font-bold text-gray-700">{{ value }}:</span>







                <div>



                  {% if value == 'Feliz' %}



                    Representa momentos de alegria, contentamento ou satisfação com a vida. É um estado positivo de bem-estar emocional.



                  {% elif value == 'Calmo' %}



                    Indica tranquilidade, serenidade e uma sensação de paz interior, sem grandes agitações emocionais.



                  {% elif value == 'Ansioso' %}



                    Expressa preocupação, nervosismo ou estresse. Pode ser um estado de alerta em relação a eventos futuros.



                  {% elif value == 'Triste' %}



                    Reflete sentimentos de melancolia, tristeza ou desânimo, geralmente associados a situações de perda ou dificuldades.



                  {% elif value == 'Irritado' %}



                    Representa frustração, raiva ou impaciência, geralmente como resposta a algo que incomoda ou causa desconforto.



                  {% endif %}



                </div>



              </div>



            {% endfor %}



          </div>



        </div>



      </div>



    </div>



  </div>







  <script>



    // Função JavaScript para gerenciar a seleção de humor



    function selectHumor(humorValue, element) {



      // 1. Remove a classe de seleção de todos os containers



      // CORREÇÃO: Usando o seletor \[data-humor-container] que foi adicionado ao HTML.



      document.querySelectorAll('\[data-humor-container]').forEach(function (el) {



        el.classList.remove('selected-humor')



      })



 



      // 2. Adiciona a classe de seleção ao elemento clicado (o container div)



      element.classList.add('selected-humor')



 



      // 3. ENCONTRA O INPUT DE RÁDIO CORRESPONDENTE E O MARCA COMO CHECADO



      const radioInputs = document.querySelectorAll('input\[name="estado"]\[type="radio"]')



 



      let found = false



 



      radioInputs.forEach(function (input) {



        if (input.value === humorValue) {



          input.checked = true



          found = true



        } else {



          input.checked = false



        }



      })



 



      if (!found) {



        console.warn(`Aviso: O input de rádio para o valor "${humorValue}" não foi encontrado. O form pode falhar.`)



      }



    }



 



    document.addEventListener('DOMContentLoaded', function () {



      // Define a data atual se o campo estiver vazio (mantido)



      const dateInput = document.getElementById('id\_data')



 



      if (dateInput \&\& !dateInput.value) {



        const today = new Date()



 



        const yyyy = today.getFullYear()



 



        let mm = today.getMonth() + 1



 



        let dd = today.getDate()



 



        if (mm < 10) mm = '0' + mm



 



        if (dd < 10) dd = '0' + dd



 



        dateInput.value = yyyy + '-' + mm + '-' + dd



      }



 



      // ------------------------------------------------------------------



      // Lógica de Pré-Seleção e Marcação Inicial



      // ------------------------------------------------------------------



 



      // Localiza o rádio que o Django marcou como 'checked' (se for uma edição ou validação falha)



      const checkedRadio = document.querySelector('input\[name="estado"]\[type="radio"]:checked')



 



      let preSelectedValue = null



 



      if (checkedRadio) {



        // Se o Django já marcou um rádio (edição/validação), usamos esse valor.



        preSelectedValue = checkedRadio.value



      }



 



      // Inicializa o estilo do container selecionado APENAS SE HOUVER UM VALOR PRÉ-SELECIONADO



      if (preSelectedValue) {



        const initialElement = document.querySelector(`\\\[data-humor-value="${preSelectedValue}"]`)



 



        if (initialElement) {



          // Chama a função de seleção para aplicar as classes CSS e marcar o rádio



          selectHumor(preSelectedValue, initialElement)



        }



      } else {



        // Garante que NENHUM rádio esteja marcado no carregamento para novos registros



        document.querySelectorAll('input\[name="estado"]\[type="radio"]').forEach(function (input) {



          input.checked = false



        })



      }



    })



  </script>



{% endblock %}







/\* homeLyfesync.css\*/



/\* ------------------------------------------------------------------- \*/







/\* VARIÁVEIS DE TEMA \*/



:root {



    --lyfesync-red-salvar: #E5534B;



    /\* Laranja/Vermelho principal (Salvar, Alerta, Alterar) \*/



    --lyfesync-green: #48BB78;



    /\* Verde primário (Autocuidado) \*/



    --lyfesync-text-emerald: #10B981;



    /\* Verde esmeralda (Humor, Detalhes de Seleção) \*/



    --lyfesync-gray-input: #E9ECEF;



    --lyfesync-text-gray: #4A5568;







    /\* VARIÁVEIS PARA O RELATÓRIO DE HUMOR \*/



    --mood-great: var(--lyfesync-green);



    --mood-good: var(--lyfesync-text-emerald);



    --mood-ok: #F6E05E;



    --mood-sad: #4299E1;



    --mood-angry: var(--lyfesync-red-salvar);



}







/\* ========================================================= \*/



/\* --- DIMENSIONAMENTO DE IMAGENS E ÍCONES (CONSOLIDADO) --- \*/



/\* ========================================================= \*/







/\* Ícones de Autocuidado no Menu (50px) - CORREÇÃO DE SELETOR \*/



.autocuidado-icon-lg {



    max-width: 8% !important;



    width: 50px;



    height: 50px;



    object-fit: contain;



}







/\* Ícones de Humor (48px) no formulário \*/



.humor-image-lg {



    width: 48px;



    height: 48px;



    object-fit: contain;



    margin-bottom: 0.5rem;



}







/\* Ícones pequenos (Humor, Gratidão, Genérico) (30px) - Consolidação \*/



.humor-image-sm,



.gratidao-icon-size,



.img-small {



    width: 30px;



    height: 30px;



    object-fit: contain;



}











/\* ========================================================= \*/



/\* --- ESTILOS DE AUTOCUIDADO (Garantindo Cor e Ícones) --- \*/



/\* ========================================================= \*/







/\* Título H2 do Menu de Autocuidado: Cor verde #48BB78 \*/



.autocuidado-link-title {



    color: var(--lyfesync-green, #48BB78);



    /\* Garante a cor verde exata desejada \*/



}







/\* Título de Card de Dica \*/



.dica-card-title {



    color: var(--lyfesync-green, #48BB78);



}







/\* Fundo verde claro para o card de dica \*/



.dica-card-green {



    background-color: #ECFDF5;



    /\* Fundo verde muito claro \*/



    border-color: var(--lyfesync-green, #48BB78) !important;



}







/\* ========================================================= \*/



/\* --- COMPONENTES DE FORMULÁRIO GERAL (MODAL/INPUT) --- \*/



/\* ========================================================= \*/







.rs-modal-content {



    background-color: #FFFFFF;



    border-radius: 1rem;



    border: none;



}







.rs-form-control {



    background-color: var(--lyfesync-gray-input, #E9ECEF);



    border: 1px solid var(--lyfesync-gray-input, #E9ECEF);



    border-radius: 0.5rem;



    box-shadow: none !important;



    padding: 0.75rem 1rem;



    color: var(--lyfesync-text-gray, #4A5568);



}







.rs-form-control:focus {



    border-color: var(--lyfesync-green, #48BB78);



    box-shadow: 0 0 0 0.25rem rgba(72, 187, 120, 0.25) !important;



}







.custom-textarea {



    min-height: 150px;



    border-radius: 8px;



    padding: 1rem;



    font-size: 1rem;



}











/\* ========================================================= \*/



/\* --- ESTILOS PÁGINA REGISTRAR HUMOR (DETALHES DO CARD) --- \*/



/\* ========================================================= \*/







.humor-title {



    color: var(--lyfesync-text-emerald, #10B981);



    font-size: 2.25rem;



    font-weight: 700;



}







.humor-grid {



    display: flex;



    flex-wrap: wrap;



    justify-content: center;



    gap: 1rem;



    padding: 1rem 0;



}







.humor-option-card {



    display: flex;



    flex-direction: column;



    align-items: center;



    justify-content: center;



    width: 100px;



    height: 120px;



    padding: 0.5rem;



    border: 2px solid #E5E7EB;



    border-radius: 12px;



    cursor: pointer;



    transition: all 0.2s ease-in-out;



    background-color: #FFFFFF;



    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06);



}







.humor-option-card:hover {



    border-color: #34D399;



    transform: translateY(-2px);



}







/\* ESTILO ATIVO CORRIGIDO: Mais visível e com efeito sutil \*/



.humor-option-card.active {



    border-color: var(--lyfesync-text-emerald, #10B981);



    background-color: #ECFDF5;



    box-shadow: 0 0 0 4px #10B981, 0 8px 12px -3px rgba(0, 0, 0, 0.2);



    /\* Sombra mais forte \*/



    transform: scale(1.05);



    /\* Efeito sutil para confirmar seleção \*/



}







.humor-label {



    font-size: 0.875rem;



    font-weight: 500;



    color: #4B5563;



    text-align: center;



}







.humor-option-card.active .humor-label {



    font-weight: 700;



    color: var(--lyfesync-text-emerald, #10B981);



}







.humor-page-container {



    min-height: 100vh;



    padding: 2rem 1rem;



    display: flex;



    flex-direction: column;



    align-items: center;



}







@media (max-width: 640px) {



    .humor-option-card {



        flex-basis: 25%;



    }



}











/\* ========================================================= \*/



/\* --- ESTILOS PÁGINA REGISTRAR GRATIDÃO / AFIRMAÇÃO --- \*/



/\* ========================================================= \*/







/\* Gratidão \*/



.gratidao-page-container {



    min-height: 100vh;



}







.gratidao-main-title {



    font-size: 2.25rem;



}







.gratidao-textarea {



    font-size: 1.15rem !important;



    resize: none !important;



    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;



}







.gratidao-date-container {



    margin-bottom: 5rem !important;



}







.gratidao-date-label {



    font-size: 1.125rem;



}







.gratidao-date-input {



    width: 150px;



    border-radius: 0.5rem;



}







.gratidao-title-color {



    color: var(--lyfesync-red-salvar, #E5534B);



}







.gratidao-question-color {



    color: var(--lyfesync-green, #48BB78);



}







.gratidao-field-bg {



    background-color: #C6F6D5;



    border: none !important;



    box-shadow: none !important;



    min-height: 120px;



}







/\* Afirmação \*/



.afirmacao-page-container {



    min-height: 100vh;



}







.afirmacao-main-title {



    font-size: 2.25rem;



}







.afirmacao-date-label {



    font-size: 1.125rem;



}







.afirmacao-date-input {



    width: 150px;



    background-color: #BDBDBD !important;



    border-radius: 0.5rem;



    border: none !important;



    color: #4A5568 !important;



}







.afirmacao-text-container {



    max-width: 500px;



}







.afirmacao-circle-group {



    margin-bottom: 5rem !important;



}







.afirmacao-circle {



    width: 250px;



    height: 250px;



    border-radius: 50%;



    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);



    display: flex;



    align-items: center;



    justify-content: center;



}







.circle-blue {



    background-color: #C0CFF7;



}







.circle-pink {



    background-color: #F7C0C0;



}







.circle-green {



    background-color: #C0F7C9;



}







.afirmacao-textarea {



    resize: none;



    font-size: 1.25rem;



    font-style: italic;



    box-shadow: none !important;



    background: transparent;



    border: none;



    text-align: center;



}







.afirmacao-error-message {



    left: 50%;



    transform: translateX(-50%);



    white-space: nowrap;



    position: absolute;



}











/\* ========================================================= \*/



/\* --- ESTILOS DE BOTÃO (Salvar/Adicionar) --- \*/



/\* ========================================================= \*/







/\* Botão Adicionar (Geral, Vermelho) \*/



.rs-btn-adicionar {



    background-color: var(--lyfesync-red-salvar, #E5534B);



    color: #FFFFFF;



    width: 100%;



    max-width: 250px;



    padding: 0.75rem 1.5rem;



    font-weight: bold;



    text-transform: uppercase;



    font-size: 1.125rem;



    border-radius: 0.5rem;



    border: none;



    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.1);



    transition: background-color 0.2s ease;



}







.rs-btn-adicionar:hover {



    background-color: #C5443C;



}







/\* Botões de Salvar (Vermelho - Gratidão/Afirmação) \*/



.btn-salvar-gratidao,



.btn-salvar-form-afirmacao-new,



.btn-salvar-humor-red {



    background-color: var(--lyfesync-red-salvar, #E5534B) !important;



    color: #FFFFFF;



    width: 250px;



    padding: 1rem 2rem;



    font-weight: 800;



    text-transform: uppercase;



    font-size: 1.125rem;



    border-radius: 0.5rem;



    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);



    border: none;



    transition: background-color 0.2s ease;



}







.btn-salvar-gratidao:hover,



.btn-salvar-form-afirmacao-new:hover,



.btn-salvar-humor-red:hover {



    background-color: #E24F34 !important;



}





.btn-salvar-form {



    background-color: var(--lyfesync-text-emerald, #10B981);



    border: none;



    padding: 0.75rem 2rem;



    font-size: 1.125rem;



    transition: background-color 0.2s;



    color: #FFFFFF;



    font-weight: bold;



    border-radius: 0.5rem;



    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06);



}







.btn-salvar-form:hover {



    background-color: #059669;



}







.humor-btn-salvar {



    margin-top: 3rem;



    max-width: 300px;



    width: 100%;



}





.btn-warning {



    background-color: var(--lyfesync-red-salvar) !important;



    border-color: var(--lyfesync-red-salvar) !important;



    color: white !important;



    transition: background-color 0.2s ease-in-out, border-color 0.2s ease-in-out;



}







.btn-warning:hover {



    background-color: #C5443C !important;



    border-color: #C5443C !important;



    color: white !important;



    opacity: 0.9;



}







.btn-warning:focus {



    box-shadow: 0 0 0 0.25rem rgba(229, 83, 75, 0.5) !important;



}





/\* --- ESTILOS RELATÓRIO DE HUMOR (MOOD TRACKER) --- \*/





.mood-report-header {



    font-size: 1.5rem;



    font-weight: 700;



    padding: 1.5rem 0;



}







.mood-header-title {



    color: var(--lyfesync-green);



}







.mood-header-month {



    color: var(--lyfesync-red-salvar);



}







.mood-report-table {



    table-layout: fixed;



    width: 100%;



    border-collapse: collapse;



    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);



    border-radius: 0.75rem;



    overflow: hidden;



    background-color: #FFFFFF;



}







.mood-report-table thead th {



    background-color: #F7FAFC;



    font-weight: 600;



    color: var(--lyfesync-text-gray);



    padding: 0.75rem 0.2rem;



    border: 1px solid #E2E8F0;



    font-size: 0.8rem;



    vertical-align: middle;



    white-space: nowrap;



}







.mood-report-table tbody td {



    height: 48px;



    padding: 0;



    border: 1px solid #E2E8F0;



    vertical-align: middle;



}







.col-humor {



    width: 100px;



    background-color: #FEFCE8;



    padding: 0.5rem;



}







.col-day {



    width: 2.5%;



    text-align: center;



}







.col-result {



    width: 80px;



}







.mood-icon-cell svg {



    width: 40px;



    height: 40px;



    vertical-align: middle;



    display: block;



    margin: 0 auto;



}







.mood-fill {



    width: 100%;



    height: 100%;



    display: block;



}







.mood-fill-great {



    background-color: var(--mood-great);



}







.mood-fill-good {



    background-color: var(--mood-good);



}







.mood-fill-ok {



    background-color: var(--mood-ok);



}







.mood-fill-sad {



    background-color: var(--mood-sad);



}







.mood-fill-angry {



    background-color: var(--mood-angry);



}







@media (max-width: 768px) {



    .mood-report-header {



        font-size: 1.1rem;



    }







    .mood-report-table thead th {



        font-size: 0.6rem;



        padding: 0.5rem 0.1rem;



    }







    .col-humor {



        width: 60px;



        padding: 0.2rem;



    }







    .mood-icon-cell svg {



        width: 30px;



        height: 30px;



    }







    .col-result {



        width: 60px;



    }



}





.humor-list-item-hover:hover {



    background-color: #e9ecef !important;



    /\* Um cinza mais claro \*/



    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);



}

