# Readme

### Projeto de laboratório de compiladores - MC911
#### Primeiro semestre de 2017

#### Professor:
Marcio Machado Pereira

#### Projeto criado por:
Luiz Fernando Cirigliano            RA 136734
João Guilherme Daros Fidelis    RA  136242

### Execução

Para executar o script em python para compilar um programa na lingua LYA, eis o comando:

```sh
$ python3 run.py <nome do arquivo>
```

python3 run.py <nome do arquivo>

Exemplo:

```sh
$ python3 run.py examples/arm.lya
```

### Vizualizando a AST gerada pelo Parser:

Após executar o script em run.py, na mesma pasta do arquivo será gerado um arquivo .ast.html de mesmo nome na pasta do arquvio utilizado como entrada.
No exemplo acima, geraria dentro da pasta examples, um arquivo chamado "arm.lya.ast.html". Basta abrir esse arquivo. Um exemplo de como abrir o arquivo html gerado:

```sh
$ xdg-open examples/arm.lya.ast.html
```

Essa AST terá os nós azuis aqueles que não tem erro nenhum e em vermelho aqueles errados ou que contém algum erro semântico.
Ou seja, caso a raíz do programa contenha um nó azul, o programa foi compilado sem erros.

### Testes

Para executar toda a pasta de exemplos de maneira rápida, criamos um script que agiliza todo o processo.
Basta executar o script run_all.sh, como abaixo:

```sh
$ ./run_all.sh
```

Todos os arquivos .lya de dentro da pasta examples serão compilados e será gerado um arquivo index.html que quando aberto, contém links para todas as AST dos exemplos que acabaram de ser geradas.
