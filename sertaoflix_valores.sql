USE `sertaoflix`;

-- Desativa temporariamente as checagens para garantir uma inserção limpa
SET FOREIGN_KEY_CHECKS = 0;

-- fazer novas entradas de sessão, historifo funcionario, salas,ingresso, avalia e clientes

-- -----------------------------------------------------
-- População da Tabela `cinema`
-- -----------------------------------------------------

 INSERT IGNORE   INTO `cinema` (`id_Cinema`, `Nome`, `CNPJ`, `Telefone`, `Endereco`, `Qnt_salas`, `Capacidade_total`, `Acessibilidade_PCD`, `VIP`) VALUES
(1, 'SertãoFlix Central', '12345678000101', '88999991111', 'Rua Central, 100', 5, 500, 1, 1),
(2, 'SertãoFlix Norte', '12345678000202', '88999992222', 'Av. Norte, 250', 3, 300, 1, 0),
(3, 'SertãoFlix Sul', '12345678000303', '88999993333', 'Praça do Sul, 15', 4, 400, 0, 1),
(4, 'SertãoFlix Sertão', '12345678000404', '88999994444', 'Rodovia do Sol, Km 5', 2, 180, 1, 0),
(5, 'SertãoFlix Praia', '12345678000505', '88999995555', 'Av. Beira Mar, 1010', 6, 700, 1, 1);

-- -----------------------------------------------------
-- População da Tabela `cliente`
-- -----------------------------------------------------
-- Nota: O campo 'Idade' é gerado virtualmente, não precisamos passar no  INSERT IGNORE .

 INSERT IGNORE  INTO `cliente` (`id_Cliente`, `Nome`, `Nascimento`, `Nivel_fidelidade`, `Email`, `Total_ingresso`) VALUES
(1, 'João Silva', '1990-05-15', 'Ouro', 'joao.silva@email.com', 12),
(2, 'Maria Oliveira', '1985-08-22', 'Prata', 'maria.oliveira@email.com', 6),
(3, 'Pedro Santos', '2002-11-03', 'Bronze', 'pedro.santos@email.com', 2),
(4, 'Ana Costa', '1998-02-28', 'Ouro', 'ana.costa@email.com', 20),
(5, 'Carlos Souza', '2005-07-12', 'Bronze', 'carlos.souza@email.com', 1);

-- -----------------------------------------------------
-- População da Tabela `sessao`
-- -----------------------------------------------------

 INSERT IGNORE  INTO `sessao` (`id_Sessao`, `Duracao_da_sala`, `Horario`, `Valor_Ingresso`, `Desconto`) VALUES
(1, 150, '2026-06-10 14:00:00', 30, 0),
(2, 180, '2026-06-11 17:30:00', 40, 5),
(3, 140, '2026-06-12 20:45:00', 35, 10),
(4, 160, '2026-06-13 15:00:00', 30, 0),
(5, 130, '2026-06-14 19:00:00', 45, 15);


-- -----------------------------------------------------
-- População da Tabela `funcionarios`
-- -----------------------------------------------------
 INSERT IGNORE  INTO `funcionarios` (`id_Funcionarios`, `Nome`, `Nascimento`, `Funcao`, `Cinema`, `Genero`, `Salario`, `cinema_id_Cinema`) VALUES
(1, 'Lucas Lima', '1994-03-10', 'Gerente', 'SertãoFlix Central', 1, 4500, 1),
(2, 'Beatriz Reis', '2000-09-25', 'Atendente', 'SertãoFlix Norte', 2, 1800, 2),
(3, 'Ricardo Rocha', '1988-12-05', 'Técnico de Projeção', 'SertãoFlix Sul', 1, 3200, 3),
(4, 'Juliana Mendes', '2003-06-14', 'Bilheteira', 'SertãoFlix Sertão', 2, 1700, 4),
(5, 'Fernando Alencar', '1997-01-30', 'Supervisor', 'SertãoFlix Praia', 1, 2800, 5);

-- -----------------------------------------------------


-- -----------------------------------------------------
-- População da Tabela `ingresso`
-- -----------------------------------------------------
 INSERT IGNORE  INTO `ingresso` (`id_Ingresso`, `Valor`, `Assento`, `Data_de_compra`, `id_cliente`, `id_sessao`, `Tipo_Desconto`) VALUES
(1, 30, 'A1', '2026-06-25 10:00:00', 1, 1, 'Nenhum'),
(2, 35, 'B4', '2026-06-25 11:30:00', 2, 2, 'Estudante'),
(3, 25, 'C2', '2026-06-25 14:15:00', 3, 3, 'Meia Idoso'),
(4, 30, 'A3', '2026-06-25 16:00:00', 4, 4, 'Nenhum'),
(5, 40, 'F5', '2026-06-25 18:45:00', 5, 5, 'Fidelidade');

-- -----------------------------------------------------
-- População da Tabela `salas`
-- -----------------------------------------------------
 INSERT IGNORE  INTO `salas` (`id_Salas`, `Numero_Sala`, `Tipo`, `Tamanho`, `Sistema_som`, `Projecao`, `Fileiras`, `Status`, `sessao_id_Sessao`, `cinema_id_Cinema`) VALUES
(1, 1, 'IMAX', 200, 'Dolby Atmos', 'Laser 4K', 15, 'Ativa', 1, 1),
(2, 2, '3D', 120, 'Dolby Digital', 'Digital', 10, 'Ativa', 2, 2),
(3, 1, 'VIP', 80, 'DTS:X', 'Laser', 8, 'Ativa', 3, 3),
(4, 1, 'Convencional', 100, 'Stereo', 'Digital', 10, 'Em Manutenção', 4, 4),
(5, 3, 'MacroXE', 250, 'Dolby Atmos', '4K', 18, 'Ativa', 5, 5);

-- -----------------------------------------------------
-- População da Tabela `ingresso_cliente`
-- -----------------------------------------------------
 INSERT IGNORE  INTO `ingresso_cliente` (`ingresso_id_Ingresso`, `cliente_id_Cliente`) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5);




-- -----------------------------------------------------
-- População da Tabela `avalia`
-- -----------------------------------------------------
 INSERT IGNORE  INTO `avalia` (`id_Avalia`, `Nota`, `Comentario`, `cliente_id_Cliente`) VALUES
(1, 9.5, 'Excelente filme! Ri do início ao fim.', 1),
(2, 8.0, 'Efeitos visuais incríveis e boa história.', 2),
(3, 7.2, 'Um pouco violento, mas a atuação foi ótima.', 3),
(4, 9.0, 'Muito divertido, bom para ir com a família.', 4),
(5, 6.5, 'Achei o ritmo um pouco arrastado no meio.', 5);



-- -----------------------------------------------------
-- População da Tabela `Telefone`
-- -----------------------------------------------------
 INSERT IGNORE  INTO `Telefone` (`idTelefone`, `Telefone`, `id_Cliente`) VALUES
(1, '11988887777', 1),
(2, '21977776666', 2),
(3, '81966665555', 3),
(4, '85955554444', 4),
(5, '88944443333', 5);

-- -----------------------------------------------------
-- População da Tabela `Endereço`
-- -----------------------------------------------------
 INSERT IGNORE  INTO `Endereço` (`id_Endereço`, `Rua`, `Numero`, `cinema_id_Cinema`) VALUES
(1, 'Rua Central', 100, 1),
(2, 'Avenida Norte', 250, 2),
(3, 'Praça do Sul', 15, 3),
(4, 'Rodovia do Sol Km 5', 5, 4),
(5, 'Avenida Beira Mar', 1010, 5);

-- Reativa as checagens de chaves estrangeiras
SET FOREIGN_KEY_CHECKS = 1;