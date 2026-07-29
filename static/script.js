(function () {
  'use strict';

  const PERIODO_LABEL = {
    dia: 'Dia',
    semana: 'Semana',
    quinzena: 'Quinzena',
    mes: 'Mês',
    ano: 'Ano',
  };

  // ---- elements: formulário principal ----
  const form = document.getElementById('production-form');
  const tipoProdutoEl = document.getElementById('tipo-produto');
  const quantidadeEl = document.getElementById('quantidade');
  const tipoServicoEl = document.getElementById('tipo-servico');
  const materialEl = document.getElementById('material');
  const furosEl = document.getElementById('furos');
  const valorDuziaRow = document.getElementById('valor-duzia-row');
  const valorDuziaManualEl = document.getElementById('valor-duzia-manual');
  const valorDuziaHintEl = document.getElementById('valor-duzia-hint');
  const dataEl = document.getElementById('data');
  const periodoEl = document.getElementById('periodo');
  const pagamentoHiddenEl = document.getElementById('pagamento');
  const toggleGroup = document.getElementById('pagamento-toggle');
  const tagNumberEl = document.getElementById('tag-number');
  const formNoteEl = document.getElementById('form-note');
  const btnClear = document.getElementById('btn-clear');
  const logBody = document.getElementById('log-body');
  const logEmpty = document.getElementById('log-empty');
  const logCount = document.getElementById('log-count');
  const previewRow = document.getElementById('preview-row');
  const previewValueEl = document.getElementById('preview-value');

  // ---- elements: summary bar ----
  const summaryDuzias = document.getElementById('summary-duzias');
  const summaryTotal = document.getElementById('summary-total');
  const summaryQuitado = document.getElementById('summary-quitado');
  const summaryPendente = document.getElementById('summary-pendente');

  // ---- elements: modal ----
  const btnAbrirPrecos = document.getElementById('btn-abrir-precos');
  const btnFecharPrecos = document.getElementById('btn-fechar-precos');
  const modalPrecos = document.getElementById('modal-precos');
  const modalTabs = document.querySelectorAll('.modal-tab');
  const tabPanelPrecos = document.getElementById('tab-panel-precos');
  const tabPanelEtapas = document.getElementById('tab-panel-etapas');

  // ---- elements: aba Tabela de preços ----
  const precoNoteEl = document.getElementById('preco-note');
  const matrixHead = document.getElementById('matrix-precos-head');
  const matrixBody = document.getElementById('matrix-precos-body');

  // ---- elements: aba Etapas ----
  const formNovaEtapa = document.getElementById('form-nova-etapa');
  const novaEtapaNome = document.getElementById('nova-etapa-nome');
  const novaEtapaDescricao = document.getElementById('nova-etapa-descricao');
  const etapaNoteEl = document.getElementById('etapa-note');
  const etapasBody = document.getElementById('etapas-body');
  const etapasEmpty = document.getElementById('etapas-empty');

  // Caches locais para calcular a prévia sem bater na API a cada tecla
  let materiaisCache = [];
  let furosCache = [];
  let tabelaPrecosCache = []; // [{material_id, material_nome, precos: [{furos, valor_duzia}]}]

  // ---------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------
  function formatBRL(valor) {
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  }

  function formatDateBR(isoDate) {
    if (!isoDate) return '—';
    const [y, m, d] = isoDate.split('-');
    return `${d}/${m}/${y}`;
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  let noteTimeout = null;
  function showNote(el, message, isError) {
    el.textContent = message;
    el.classList.toggle('error', Boolean(isError));
    clearTimeout(noteTimeout);
    if (message) {
      noteTimeout = setTimeout(() => {
        el.textContent = '';
        el.classList.remove('error');
      }, 5000);
    }
  }

  async function apiFetch(url, options) {
    let response;
    try {
      response = await fetch(url, options);
    } catch (networkErr) {
      throw new Error('Não foi possível conectar ao servidor. Verifique se o Flask está rodando.');
    }
    let body = null;
    try {
      body = await response.json();
    } catch (parseErr) {
      // resposta sem corpo JSON — tudo bem
    }
    if (!response.ok) {
      const mensagem = (body && body.erro) || `Erro inesperado (HTTP ${response.status}).`;
      throw new Error(mensagem);
    }
    return body;
  }

  // busca o preço (ou null) de uma combinação no cache local da tabela de preços
  function precoNoCache(materialId, furos) {
    const linha = tabelaPrecosCache.find((l) => String(l.material_id) === String(materialId));
    if (!linha) return null;
    const cell = linha.precos.find((p) => String(p.furos) === String(furos));
    return cell ? cell.valor_duzia : null;
  }

  // ---------------------------------------------------------------------
  // Pagamento toggle
  // ---------------------------------------------------------------------
  function setPagamento(value) {
    pagamentoHiddenEl.value = value;
    toggleGroup.querySelectorAll('.toggle-btn').forEach((btn) => {
      btn.setAttribute('aria-checked', String(btn.dataset.value === value));
    });
  }

  toggleGroup.addEventListener('click', (e) => {
    const btn = e.target.closest('.toggle-btn');
    if (!btn) return;
    setPagamento(btn.dataset.value);
  });

  // ---------------------------------------------------------------------
  // Quantity stepper
  // ---------------------------------------------------------------------
  document.querySelectorAll('.qty-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const step = parseFloat(btn.dataset.step);
      const current = parseFloat(quantidadeEl.value) || 0;
      const next = Math.max(0, +(current + step).toFixed(2));
      quantidadeEl.value = next;
      atualizarCampoValor();
    });
  });

  // ---------------------------------------------------------------------
  // Campo de valor por dúzia — editável condicionalmente.
  // Aparece sempre que Material + Furos estão selecionados. Preenche
  // sozinho com o valor da tabela_precos quando existe; fica vazio e
  // com destaque quando a combinação ainda não tem preço (obrigando
  // o usuário a digitar). Em ambos os casos o campo permanece editável.
  // ---------------------------------------------------------------------
  function atualizarCampoValor() {
    const materialId = materialEl.value;
    const furos = furosEl.value;

    if (!materialId || !furos) {
      valorDuziaRow.hidden = true;
      atualizarPreview();
      return;
    }

    valorDuziaRow.hidden = false;
    const precoExistente = precoNoCache(materialId, furos);

    if (precoExistente !== null) {
      valorDuziaManualEl.value = precoExistente.toFixed(2);
      valorDuziaHintEl.textContent = '(preenchido automaticamente — pode sobrescrever)';
    } else {
      valorDuziaManualEl.value = '';
      valorDuziaHintEl.textContent = '(sem preço cadastrado ainda — informe o valor)';
      valorDuziaManualEl.focus();
    }

    atualizarPreview();
  }

  materialEl.addEventListener('change', atualizarCampoValor);
  furosEl.addEventListener('change', atualizarCampoValor);

  // ---------------------------------------------------------------------
  // Prévia de valor ao vivo
  // ---------------------------------------------------------------------
  function atualizarPreview() {
    const quantidade = parseFloat(quantidadeEl.value) || 0;
    const valorDuzia = parseFloat(valorDuziaManualEl.value);

    if (!quantidade || isNaN(valorDuzia) || valorDuzia < 0) {
      previewRow.hidden = true;
      return;
    }

    previewValueEl.textContent = formatBRL(quantidade * valorDuzia);
    previewRow.hidden = false;
  }

  quantidadeEl.addEventListener('input', atualizarPreview);
  valorDuziaManualEl.addEventListener('input', atualizarPreview);

  // ---------------------------------------------------------------------
  // Carregar selects: Etapa (tipos_servico), Material, Furos
  // ---------------------------------------------------------------------
  async function carregarSelectsPrincipais() {
    let etapas, materiais, furos;
    try {
      [etapas, materiais, furos] = await Promise.all([
        apiFetch('/api/tipos-servico?apenas_ativos=true'),
        apiFetch('/api/materiais?apenas_ativos=true'),
        apiFetch('/api/furos'),
      ]);
    } catch (err) {
      showNote(formNoteEl, err.message, true);
      return;
    }

    materiaisCache = materiais;
    furosCache = furos;

    // Etapa
    const etapaAtual = tipoServicoEl.value;
    tipoServicoEl.innerHTML = '<option value="" disabled selected>Selecione</option>';
    if (etapas.length === 0) {
      const opt = document.createElement('option');
      opt.disabled = true;
      opt.textContent = 'Nenhuma etapa cadastrada — abra "Gerenciar preços"';
      tipoServicoEl.appendChild(opt);
    } else {
      etapas.forEach((etapa) => {
        const opt = document.createElement('option');
        opt.value = etapa.id;
        const sufixo = etapa.descricao ? ` — ${etapa.descricao}` : '';
        opt.textContent = `${etapa.nome}${sufixo}`;
        if (etapa.descricao) opt.title = etapa.descricao;
        tipoServicoEl.appendChild(opt);
      });
      if (etapaAtual && etapas.some((e) => String(e.id) === String(etapaAtual))) {
        tipoServicoEl.value = etapaAtual;
      }
    }

    // Material
    const materialAtual = materialEl.value;
    materialEl.innerHTML = '<option value="" disabled selected>Selecione</option>';
    materiais.forEach((m) => {
      const opt = document.createElement('option');
      opt.value = m.id;
      opt.textContent = m.nome;
      materialEl.appendChild(opt);
    });
    if (materialAtual && materiais.some((m) => String(m.id) === String(materialAtual))) {
      materialEl.value = materialAtual;
    }

    // Furos (lista fixa vinda do backend)
    const furosAtual = furosEl.value;
    furosEl.innerHTML = '<option value="" disabled selected>Selecione</option>';
    furos.forEach((f) => {
      const opt = document.createElement('option');
      opt.value = f;
      opt.textContent = `${f} furos`;
      furosEl.appendChild(opt);
    });
    if (furosAtual && furos.some((f) => String(f) === String(furosAtual))) {
      furosEl.value = furosAtual;
    }
  }

  async function carregarTabelaPrecosCache() {
    try {
      tabelaPrecosCache = await apiFetch('/api/tabela-precos');
    } catch (err) {
      showNote(formNoteEl, err.message, true);
    }
  }

  // ---------------------------------------------------------------------
  // Renderizar tabela de registros
  // ---------------------------------------------------------------------
  async function renderLog() {
    let registros;
    try {
      registros = await apiFetch('/api/registros');
    } catch (err) {
      showNote(formNoteEl, err.message, true);
      return;
    }

    logBody.innerHTML = '';
    logEmpty.style.display = registros.length === 0 ? 'block' : 'none';

    registros.forEach((reg) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>Nº ${String(reg.id).padStart(4, '0')}</td>
        <td>${escapeHtml(reg.tipo_produto)}</td>
        <td>${reg.quantidade_duzias}</td>
        <td>${escapeHtml(reg.tipo_servico_nome)}</td>
        <td>${escapeHtml(reg.material_nome)}</td>
        <td>${reg.furos}</td>
        <td>${formatBRL(reg.valor_duzia_aplicado)}</td>
        <td><strong>${formatBRL(reg.valor_total)}</strong></td>
        <td>${formatDateBR(reg.data)}</td>
        <td>${PERIODO_LABEL[reg.periodo] || reg.periodo}</td>
        <td>
          <button type="button" class="pill pill-${reg.pagamento} pill-toggle" data-id="${reg.id}" data-atual="${reg.pagamento}">
            ${reg.pagamento}
          </button>
        </td>
        <td><button type="button" class="row-delete" data-id="${reg.id}" aria-label="Excluir registro">✕</button></td>
      `;
      logBody.appendChild(tr);
    });

    logCount.textContent = `${registros.length} ${registros.length === 1 ? 'item' : 'itens'}`;
    tagNumberEl.textContent = 'Nº ' + String(registros.length + 1).padStart(4, '0');

    await atualizarResumoDia();
  }

  logBody.addEventListener('click', async (e) => {
    const pillBtn = e.target.closest('.pill-toggle');
    if (pillBtn) {
      const novoEstado = pillBtn.dataset.atual === 'quitado' ? 'pendente' : 'quitado';
      try {
        await apiFetch(`/api/registros/${pillBtn.dataset.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pagamento: novoEstado }),
        });
        await renderLog();
      } catch (err) {
        showNote(formNoteEl, err.message, true);
      }
      return;
    }

    const delBtn = e.target.closest('.row-delete');
    if (delBtn) {
      try {
        await apiFetch(`/api/registros/${delBtn.dataset.id}`, { method: 'DELETE' });
        await renderLog();
      } catch (err) {
        showNote(formNoteEl, err.message, true);
      }
    }
  });

  // ---------------------------------------------------------------------
  // Resumo da diária
  // ---------------------------------------------------------------------
  async function atualizarResumoDia() {
    const dataRef = dataEl.value || new Date().toISOString().slice(0, 10);
    let resumo;
    try {
      resumo = await apiFetch(`/api/resumo-dia?data=${encodeURIComponent(dataRef)}`);
    } catch (err) {
      return;
    }

    summaryDuzias.textContent = resumo.total_duzias.toLocaleString('pt-BR');
    summaryTotal.textContent = formatBRL(resumo.total_valor);
    summaryQuitado.textContent = formatBRL(resumo.total_quitado);
    summaryPendente.textContent = formatBRL(resumo.total_pendente);
  }

  dataEl.addEventListener('change', atualizarResumoDia);

  // ---------------------------------------------------------------------
  // Submissão do formulário principal
  // ---------------------------------------------------------------------
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!form.checkValidity()) {
      form.reportValidity();
      showNote(formNoteEl, 'Preencha os campos obrigatórios antes de salvar.', true);
      return;
    }

    const valorDigitado = valorDuziaManualEl.value.trim();
    if (valorDigitado === '') {
      showNote(formNoteEl, 'Informe o valor por dúzia (a combinação selecionada ainda não tem preço salvo, ou o campo foi limpo).', true);
      valorDuziaManualEl.focus();
      return;
    }

    const payload = {
      tipo_produto: tipoProdutoEl.value.trim(),
      quantidade_duzias: parseFloat(quantidadeEl.value),
      tipo_servico_id: tipoServicoEl.value,
      material_id: materialEl.value,
      furos: furosEl.value,
      valor_duzia_manual: parseFloat(valorDigitado),
      data: dataEl.value,
      periodo: periodoEl.value,
      pagamento: pagamentoHiddenEl.value,
    };

    try {
      await apiFetch('/api/registros', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch (err) {
      showNote(formNoteEl, err.message, true);
      return;
    }

    showNote(formNoteEl, 'Registro salvo.');
    resetForm();
    await carregarTabelaPrecosCache(); // o valor pode ter atualizado a tabela
    await renderLog();
  });

  function resetForm() {
    tipoProdutoEl.value = '';
    quantidadeEl.value = 0;
    tipoServicoEl.selectedIndex = 0;
    setPagamento('pendente');
    previewRow.hidden = true;
    tipoProdutoEl.focus();
    // Propositalmente NÃO limpa Data, Período, Material e Furos — é comum
    // registrar vários produtos seguidos, no mesmo dia, mesmo período,
    // e frequentemente mesmo material/furos (ex: um lote inteiro de Pete
    // 20 furos passando por etapas diferentes). Isso economiza toques
    // repetidos. O valor por dúzia é recalculado no próximo change.
  }

  btnClear.addEventListener('click', () => {
    resetForm();
    showNote(formNoteEl, 'Campos limpos.');
  });

  // ---------------------------------------------------------------------
  // Modal: abrir/fechar + abas
  // ---------------------------------------------------------------------
  function abrirModalPrecos() {
    modalPrecos.hidden = false;
    renderMatrixPrecos();
    renderEtapas();
  }

  function fecharModalPrecos() {
    modalPrecos.hidden = true;
  }

  btnAbrirPrecos.addEventListener('click', abrirModalPrecos);
  btnFecharPrecos.addEventListener('click', fecharModalPrecos);
  modalPrecos.addEventListener('click', (e) => {
    if (e.target === modalPrecos) fecharModalPrecos();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modalPrecos.hidden) fecharModalPrecos();
  });

  modalTabs.forEach((tabBtn) => {
    tabBtn.addEventListener('click', () => {
      modalTabs.forEach((t) => t.setAttribute('aria-selected', 'false'));
      tabBtn.setAttribute('aria-selected', 'true');
      const tab = tabBtn.dataset.tab;
      tabPanelPrecos.hidden = tab !== 'precos';
      tabPanelEtapas.hidden = tab !== 'etapas';
    });
  });

  // ---------------------------------------------------------------------
  // Aba: Tabela de preços (matriz Material x Furos, células clicáveis)
  // ---------------------------------------------------------------------
  async function renderMatrixPrecos() {
    let tabela, furos;
    try {
      [tabela, furos] = await Promise.all([
        apiFetch('/api/tabela-precos'),
        apiFetch('/api/furos'),
      ]);
    } catch (err) {
      showNote(precoNoteEl, err.message, true);
      return;
    }

    tabelaPrecosCache = tabela;

    // cabeçalho: Material + uma coluna por quantidade de furos
    matrixHead.innerHTML = '<th>Material</th>' + furos.map((f) => `<th>${f} furos</th>`).join('');

    matrixBody.innerHTML = '';
    tabela.forEach((linha) => {
      const tr = document.createElement('tr');
      const celulasHtml = linha.precos.map((p) => {
        const temPreco = p.valor_duzia !== null;
        const texto = temPreco ? formatBRL(p.valor_duzia) : 'definir';
        const classeExtra = temPreco ? '' : ' matrix-cell--empty';
        return `<td>
          <button type="button" class="matrix-cell-btn${classeExtra}"
            data-material-id="${linha.material_id}"
            data-material-nome="${escapeHtml(linha.material_nome)}"
            data-furos="${p.furos}"
            data-valor="${temPreco ? p.valor_duzia : ''}">
            ${texto}
          </button>
        </td>`;
      }).join('');
      tr.innerHTML = `<td>${escapeHtml(linha.material_nome)}</td>${celulasHtml}`;
      matrixBody.appendChild(tr);
    });
  }

  matrixBody.addEventListener('click', async (e) => {
    const btn = e.target.closest('.matrix-cell-btn');
    if (!btn) return;

    const materialId = btn.dataset.materialId;
    const materialNome = btn.dataset.materialNome;
    const furos = btn.dataset.furos;
    const valorAtual = btn.dataset.valor;

    const entrada = window.prompt(
      `Valor por dúzia — ${materialNome}, ${furos} furos (R$):`,
      valorAtual || ''
    );
    if (entrada === null) return;

    const novoValor = parseFloat(entrada.replace(',', '.'));
    if (isNaN(novoValor) || novoValor < 0) {
      showNote(precoNoteEl, 'Valor inválido.', true);
      return;
    }

    try {
      await apiFetch('/api/tabela-precos', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ material_id: materialId, furos, valor_duzia: novoValor }),
      });
      showNote(precoNoteEl, `Preço de ${materialNome} / ${furos} furos atualizado.`);
      await renderMatrixPrecos();
      // se a combinação editada é a que está selecionada no formulário
      // principal agora, atualiza o campo de valor também
      if (String(materialEl.value) === String(materialId) && String(furosEl.value) === String(furos)) {
        atualizarCampoValor();
      }
    } catch (err) {
      showNote(precoNoteEl, err.message, true);
    }
  });

  // ---------------------------------------------------------------------
  // Aba: Etapas do processo (CRUD simples, sem preço)
  // ---------------------------------------------------------------------
  async function renderEtapas() {
    let etapas;
    try {
      etapas = await apiFetch('/api/tipos-servico');
    } catch (err) {
      showNote(etapaNoteEl, err.message, true);
      return;
    }

    etapasBody.innerHTML = '';
    etapasEmpty.style.display = etapas.length === 0 ? 'block' : 'none';

    etapas.forEach((etapa) => {
      const tr = document.createElement('tr');
      const statusClass = etapa.ativo ? 'status-badge--ativo' : 'status-badge--inativo';
      const statusTexto = etapa.ativo ? 'Ativo' : 'Inativo';
      const acaoTexto = etapa.ativo ? 'Desativar' : 'Reativar';
      const descricaoHtml = etapa.descricao
        ? `<span class="servico-descricao">${escapeHtml(etapa.descricao)}</span>`
        : '';

      tr.innerHTML = `
        <td>
          <span class="servico-nome">${escapeHtml(etapa.nome)}</span>
          ${descricaoHtml}
        </td>
        <td><span class="status-badge ${statusClass}">${statusTexto}</span></td>
        <td>
          <div class="row-actions">
            <button type="button" class="row-action-btn" data-action="alternar" data-id="${etapa.id}" data-ativo="${etapa.ativo}">${acaoTexto}</button>
            <button type="button" class="row-action-btn danger" data-action="excluir" data-id="${etapa.id}">Excluir</button>
          </div>
        </td>
      `;
      etapasBody.appendChild(tr);
    });

    // o select do formulário principal pode ter mudado (etapa nova/desativada)
    await carregarSelectsPrincipais();
  }

  etapasBody.addEventListener('click', async (e) => {
    const btn = e.target.closest('.row-action-btn');
    if (!btn) return;

    const id = btn.dataset.id;
    const action = btn.dataset.action;

    if (action === 'alternar') {
      const ativoAtual = btn.dataset.ativo === '1' || btn.dataset.ativo === 'true';
      try {
        await apiFetch(`/api/tipos-servico/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ativo: !ativoAtual }),
        });
        await renderEtapas();
      } catch (err) {
        showNote(etapaNoteEl, err.message, true);
      }
      return;
    }

    if (action === 'excluir') {
      const confirmado = window.confirm(
        'Excluir esta etapa? Se ela já tiver sido usada em registros, será apenas desativada.'
      );
      if (!confirmado) return;
      try {
        const resultado = await apiFetch(`/api/tipos-servico/${id}`, { method: 'DELETE' });
        showNote(etapaNoteEl, resultado.mensagem || 'Etapa excluída.');
        await renderEtapas();
      } catch (err) {
        showNote(etapaNoteEl, err.message, true);
      }
    }
  });

  formNovaEtapa.addEventListener('submit', async (e) => {
    e.preventDefault();

    const nome = novaEtapaNome.value.trim();
    const descricao = novaEtapaDescricao.value.trim();

    if (!nome) {
      showNote(etapaNoteEl, 'Informe o nome da etapa.', true);
      return;
    }

    try {
      await apiFetch('/api/tipos-servico', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, descricao }),
      });
    } catch (err) {
      showNote(etapaNoteEl, err.message, true);
      return;
    }

    showNote(etapaNoteEl, `"${nome}" adicionada.`);
    novaEtapaNome.value = '';
    novaEtapaDescricao.value = '';
    novaEtapaNome.focus();
    await renderEtapas();
  });

  // ---------------------------------------------------------------------
  // Init
  // ---------------------------------------------------------------------
  (async function init() {
    setPagamento('pendente');
    dataEl.value = new Date().toISOString().slice(0, 10);
    await carregarTabelaPrecosCache();
    await carregarSelectsPrincipais();
    await renderLog();
  })();
})();
