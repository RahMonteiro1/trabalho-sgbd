# Documentação do formato binário

## 1. Visão geral

O arquivo binário armazena as informações necessárias para reconstruir o sistema: usuários, permissões, bancos de dados, tabelas, atributos, chaves e registros.

Os campos são gravados sequencialmente, sem separadores, nesta ordem:

1. quantidade de usuários e dados de cada usuário;
2. quantidade de bancos e dados de cada banco;
3. para cada banco, quantidade de tabelas e dados de cada tabela;
4. para cada tabela, quantidade de registros e valores de cada registro.

A leitura segue exatamente a mesma ordem, e as quantidades indicam quantos elementos devem ser lidos em cada lista.

A implementação utiliza `struct.pack` para converter valores em bytes e `struct.unpack` para fazer a conversão inversa. O arquivo é aberto em modo binário: `wb` para gravação e `rb` para leitura, enquanto mecanismos como `pickle` não são utilizados.

A gravação é feita primeiro em um arquivo temporário (`caminho.tmp`). Somente depois que todo o conteúdo foi gravado sem erro, o temporário substitui o arquivo original com `os.replace`. Assim, se algum valor não puder ser gravado, o arquivo anterior permanece intacto. Se a gravação falhar, o arquivo temporário parcial fica na pasta e é sobrescrito no próximo salvamento.

## 2. Tipos básicos

Todos os campos do arquivo são representados por quatro tipos básicos:

| Tipo | Formato `struct` | Tamanho | Representação |
|---|---:|---:|---|
| `INT` | `<q` | 8 bytes | Inteiro com sinal de 64 bits, little-endian |
| `FLOAT` | `<d` | 8 bytes | Ponto flutuante de 64 bits (double), little-endian |
| `BOOL` | `<?` | 1 byte | `00` = falso; `01` = verdadeiro |
| `STR` | `<1024s` | 1024 bytes | Texto UTF-8, completado com bytes `00` |

O prefixo `<` determina a ordem little-endian e impede a inserção de bytes de alinhamento. Assim, os tamanhos dos campos são definidos pelo formato e não dependem da arquitetura da máquina.

Exemplos de representação:

| Valor | Bytes em hexadecimal |
|---|---|
| `INT` 25 | `19 00 00 00 00 00 00 00` |
| `FLOAT` 8.5 | `00 00 00 00 00 00 21 40` |
| `BOOL` verdadeiro | `01` |
| `STR` `"Ana"` | `41 6E 61`, seguido de 1021 bytes `00` |

O tipo `FLOAT` preserva a representação binária de 64 bits usada pelo Python, mas não elimina aproximações inerentes a números decimais representados em ponto flutuante, enquanto o tipo `INT` aceita valores de −2⁶³ a 2⁶³−1.

## 3. Limites e regras de representação

| Tipo | Limite |
|---|---|
| `STR` | Até 1024 bytes após a codificação `UTF-8` |
| `INT` | De −2⁶³ a 2⁶³−1 |
| `FLOAT` | Valores representáveis em ponto flutuante binário de 64 bits (`NaN` e infinito são rejeitados) |
| `BOOL` | Apenas `False` ou `True` |

A contagem de `STR` é feita em bytes, não em caracteres. Por exemplo, caracteres acentuados podem ocupar mais de um byte em `UTF-8`. O gravador deve rejeitar textos cuja codificação ultrapasse 1024 bytes; não deve truncá-los. Também deve rejeitar textos terminados em `\x00`, pois a leitura remove os bytes zero finais para recuperar o preenchimento.

Os inteiros devem caber no intervalo de 64 bits. Os valores dos registros são validados na inserção: texto com mais de 1024 bytes em `UTF-8`, inteiro fora do intervalo de 64 bits e `FLOAT` com `NaN` ou infinito são rejeitados, e o `INSERT` não é executado. A mesma verificação de tamanho se aplica ao nome e à senha na criação de usuários. Se algum outro texto do sistema (como o nome de um banco, tabela ou atributo) ultrapassar 1024 bytes, o gravador recusa a gravação e o arquivo anterior permanece intacto.

As listas têm tamanho variável, mas são sempre precedidas por um campo `INT` que informa sua quantidade de elementos. Os campos individuais têm tamanho fixo.

## 4. Estrutura geral do arquivo

A estrutura completa é:

```text
ARQUIVO
├── qtd_usuarios                 INT
├── USUARIO × qtd_usuarios
├── qtd_bancos                   INT
└── BANCO × qtd_bancos
```

Cada quantidade é gravada como `INT` de 8 bytes.

## 5. Estrutura de USUARIO

Cada usuário é gravado nesta ordem:

| Campo | Tipo | Significado |
|---|---|---|
| `nome` | `STR` | Nome do usuário |
| `senha` | `STR` | Senha |
| `eh_admin` | `BOOL` | Indica se o usuário é administrador |
| `qtd_perm_banco` | `INT` | Quantidade de permissões associadas a bancos |
| `nome_banco` | `STR` | Banco ao qual a permissão se aplica |
| `permissao` | `STR` | Permissão concedida |
| `qtd_perm_tabela` | `INT` | Quantidade de permissões associadas a tabelas |
| `nome_banco` | `STR` | Banco que contém a tabela |
| `nome_tabela` | `STR` | Tabela à qual a permissão se aplica |
| `permissao` | `STR` | Permissão concedida |

A primeira lista guarda as permissões sobre bancos inteiros, enquanto a segunda guarda as permissões sobre tabelas específicas. Cada permissão da primeira lista é gravada em uma dupla (nome_banco, permissao) e cada permissão da segunda, em um trio (nome_banco, nome_tabela, permissao), uma após a outra.

Cada permissão é armazenada separadamente. Se um usuário possuir duas permissões sobre a mesma tabela, haverá duas entradas na lista. Quando a aplicação expande uma concessão `ALL` em permissões individuais, são gravadas essas permissões efetivas.

## 6. Estrutura de BANCO

Cada banco é gravado nesta ordem:

| Campo | Tipo |
|---|---|
| `nome` | `STR` |
| `qtd_tabelas` | `INT` |
| `TABELA × qtd_tabelas` | Estrutura descrita na seção 7 |

## 7. Estrutura de TABELA

Cada tabela é gravada nesta ordem:

| Campo | Tipo | Significado |
|---|---|---|
| `nome` | `STR` | Nome da tabela |
| `qtd_atributos` | `INT` | Quantidade de atributos |
| `nome` | `STR` | Nome de cada atributo |
| `tipo` | `STR` | Tipo de cada atributo: `INTEGER`, `FLOAT`, `STRING` ou `BOOLEAN` |
| `chave_primaria` | `STR` | Nome do atributo que é a chave primária |
| `qtd_chaves_estrangeiras` | `INT` | Quantidade de chaves estrangeiras |
| `atributo` | `STR` | Atributo local da chave estrangeira |
| `tabela_referenciada` | `STR` | Nome da tabela referenciada |
| `atributo_referenciado` | `STR` | Nome do atributo referenciado |
| `qtd_registros` | `INT` | Quantidade de registros |
| `REGISTRO × qtd_registros` | Variável conforme os tipos | Valores dos registros, conforme a seção 8 |

Cada atributo é gravado como uma dupla (nome, tipo), um par após o outro (nome1, tipo1, nome2, tipo2, ...). 

Cada chave estrangeira é gravada como um trio (atributo, tabela_referenciada, atributo_referenciado).

Os atributos são gravados antes dos registros. Assim, quando o leitor chega aos registros, já conhece a quantidade, a ordem e o tipo das colunas. A chave primária é armazenada pelo nome do atributo. Cada chave estrangeira registra o atributo local e o par formado pela tabela e pelo atributo referenciados.

## 8. Estrutura de REGISTRO e marcador de nulidade

Um registro armazena um valor para cada atributo, na mesma ordem em que os atributos foram definidos na tabela.

Cada valor é gravado com dois componentes:

1. um marcador de nulidade (`BOOL`, 1 byte);
2. o espaço reservado ao valor, conforme o tipo do atributo.

O marcador tem este significado:

| Marcador | Significado | Leitura |
|---|---|---|
| `00` | O valor não é nulo | Interpretar os bytes seguintes conforme o tipo |
| `01` | O valor é `None` | Reconstruir `None` e ignorar o espaço reservado |

Qualquer outro valor para o marcador é inválido. Quando o valor é nulo, o espaço reservado é preenchido com bytes zero. Esse espaço continua presente mesmo para valores nulos; por isso, todos os registros de uma mesma tabela têm o mesmo tamanho.

O marcador existe somente nos valores dos registros; contagens, nomes e permissões não o têm. Atualmente o interpretador de comandos não aceita `NULL`, então todos os marcadores gravados valem `00`. O campo existe para que valores nulos possam ser representados sem alterar o formato.

| Tipo do atributo | Formato por coluna | Tamanho por coluna |
|---|---|---:|
| `INTEGER` | `<?q` | 9 bytes |
| `FLOAT` | `<?d` | 9 bytes |
| `STRING` | `<?1024s` | 1025 bytes |
| `BOOLEAN` | `<??` | 2 bytes |

O formato completo de um registro é formado pelo prefixo `<` seguido dos formatos de cada coluna, na ordem definida pela tabela.

Por exemplo, para:

```text
pessoa(
    cpf INTEGER,
    nome STRING,
    idade INTEGER,
    media FLOAT
)
```

o formato é:

```text
<?q?1024s?q?d
```

O registro ocupa:

```text
(1 + 8) + (1 + 1024) + (1 + 8) + (1 + 8) = 1052 bytes
```

A leitura verifica o marcador de cada coluna. Se for `00`, interpreta o valor reservado; se for `01`, devolve `None`.

## 9. Exemplo mínimo completo em hexadecimal

Considere um sistema com:

- um usuário `Admin`, senha `123456`, identificado como administrador e sem permissões explícitas;
- um banco chamado `uni`;
- uma tabela `alunos`, com os atributos `matricula INTEGER` e `nome STRING`;
- `matricula` como chave primária;
- um registro: `(1001, "Ana")`.

O arquivo contém exatamente 10.315 bytes. Abaixo, os campos são apresentados na ordem em que aparecem no arquivo, em hexadecimal.

Para tornar a apresentação legível, sequências de bytes zero são abreviadas como `00 × N`. Essa notação significa exatamente N bytes `00` consecutivos; não representa bytes adicionais nem campos omitidos.

| Campo | Representação hexadecimal |
|---|---|
| Quantidade de usuários: 1 | `01 00 00 00 00 00 00 00` |
| Nome `Admin` | `41 64 6D 69 6E` + `00 × 1019` |
| Senha `123456` | `31 32 33 34 35 36` + `00 × 1018` |
| `eh_admin = True` | `01` |
| Quantidade de permissões de banco: 0 | `00 00 00 00 00 00 00 00` |
| Quantidade de permissões de tabela: 0 | `00 00 00 00 00 00 00 00` |
| Quantidade de bancos: 1 | `01 00 00 00 00 00 00 00` |
| Nome do banco `uni` | `75 6E 69` + `00 × 1021` |
| Quantidade de tabelas: 1 | `01 00 00 00 00 00 00 00` |
| Nome da tabela `alunos` | `61 6C 75 6E 6F 73` + `00 × 1018` |
| Quantidade de atributos: 2 | `02 00 00 00 00 00 00 00` |
| Nome do atributo `matricula` | `6D 61 74 72 69 63 75 6C 61` + `00 × 1015` |
| Tipo `INTEGER` | `49 4E 54 45 47 45 52` + `00 × 1017` |
| Nome do atributo `nome` | `6E 6F 6D 65` + `00 × 1020` |
| Tipo `STRING` | `53 54 52 49 4E 47` + `00 × 1018` |
| Nome da chave primária `matricula` | `6D 61 74 72 69 63 75 6C 61` + `00 × 1015` |
| Quantidade de chaves estrangeiras: 0 | `00 00 00 00 00 00 00 00` |
| Quantidade de registros: 1 | `01 00 00 00 00 00 00 00` |
| Marcador da matrícula (não nula) | `00` |
| Matrícula 1001 | `E9 03 00 00 00 00 00 00` |
| Marcador do nome (não nulo) | `00` |
| Texto `Ana` | `41 6E 61` + `00 × 1021` |

A soma dos tamanhos dos campos é:

```text
qtd_usuarios                         8
USUARIO                           2065
qtd_bancos                          8
BANCO + TABELA                   8234
--------------------------------------
TOTAL                            10315 bytes
```

O registro ocupa 1034 bytes: 1 byte do marcador e 8 bytes do inteiro, mais 1 byte do marcador e 1024 bytes da string.

## 10. Como a leitura reconstrói o sistema

A leitura percorre o arquivo na mesma ordem da gravação:

1. Lê os 8 bytes de `qtd_usuarios`. O valor indica quantos objetos `Usuario` deverão ser reconstruídos.
2. Para cada usuário, lê `nome`, `senha` e `eh_admin`. Em seguida, lê `qtd_perm_banco` e suas entradas; depois, `qtd_perm_tabela` e suas entradas. Com esses dados, reconstrói o usuário e suas permissões.
3. Lê os 8 bytes de `qtd_bancos`. Para cada banco, lê seu nome e `qtd_tabelas`.
4. Para cada tabela, lê seu nome, a quantidade de atributos e os pares nome/tipo. Depois, recupera a chave primária, as chaves estrangeiras e a quantidade de registros.
5. Com os tipos e a ordem dos atributos já conhecidos, determina o formato e o tamanho de cada registro.
6. Para cada coluna de cada registro, lê o marcador de nulidade. Se o marcador for `01`, acrescenta `None` à lista de valores. Se for `00`, interpreta os bytes seguintes conforme o tipo (`INTEGER`, `FLOAT`, `STRING` ou `BOOLEAN`).
7. Acrescenta os registros reconstruídos à tabela e, ao terminar suas tabelas, acrescenta o banco ao sistema.

No exemplo da seção 9, o leitor reconstrói o usuário `Admin`, o banco `uni`, a tabela `alunos` e seu registro. Para o registro, lê o marcador `00`, interpreta `E9 03 00 00 00 00 00 00` como o inteiro 1001, lê o segundo marcador `00` e recupera a string `Ana`.

Cada leitura deve confirmar que recebeu exatamente a quantidade de bytes solicitada. O carregador também deve rejeitar contagens negativas, tipos ou marcadores inválidos, dados incompletos e bytes extras depois do último campo. Se ocorrer qualquer erro, o sistema que já está em memória não deve ser substituído parcialmente: a reconstrução deve terminar com sucesso antes de atualizar as estruturas atuais. Se o arquivo não existir, o carregamento também falha e o sistema em memória não é alterado.

## 11. Informações que não são gravadas

O usuário atualmente autenticado e o banco selecionado não são gravados. Depois de carregar o arquivo, é necessário realizar novo login e selecionar novamente o banco com `USE DATABASE`.
