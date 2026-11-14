"""Script para gerar e estruturar o corpus teológico aprovado em corpus/approved/theology/."""

import json
import shutil
from pathlib import Path


def create_theology_corpus():
    root = Path(__file__).resolve().parent.parent
    target_theology_dir = root / "corpus" / "approved" / "theology"
    target_theology_dir.mkdir(parents=True, exist_ok=True)

    neuu_dir = root / "data" / "sources" / "neuu-classics" / "data" / "02_translated" / "pt"

    # 1. Copiar e enriquecer as 4 obras aprovadas do NEUU Classics
    neuu_configs = {
        "athanasius-incarnation.json": {
            "src": neuu_dir / "athanasius" / "incarnation.json",
            "completeness": "full",
            "text_type": "translation",
            "translation_method": "claude-opus-4-6 (NEUU classics dataset)",
            "license": "CC-BY-4.0",
            "provenance_url": "https://github.com/neuu-org/bible-classics-dataset",
            "human_reviewed": False,
            "notes": "Tradução integral a partir da edição clássica em Domínio Público (CCEL). Dataset editorial NEUU licenciado sob CC BY 4.0."
        },
        "anselm-meditations.json": {
            "src": neuu_dir / "anselm" / "meditations.json",
            "completeness": "full",
            "text_type": "translation",
            "translation_method": "claude-opus-4-6 (NEUU classics dataset)",
            "license": "CC-BY-4.0",
            "provenance_url": "https://github.com/neuu-org/bible-classics-dataset",
            "human_reviewed": False,
            "notes": "Meditações de Santo Anselmo de Cantuária. Tradução a partir de edição em Domínio Público (CCEL). Dataset editorial NEUU sob CC BY 4.0."
        },
        "kempis-imitation.json": {
            "src": neuu_dir / "kempis" / "imitation_book1.json",
            "completeness": "full",
            "text_type": "translation",
            "translation_method": "claude-opus-4-6 (NEUU classics dataset)",
            "license": "CC-BY-4.0",
            "provenance_url": "https://github.com/neuu-org/bible-classics-dataset",
            "human_reviewed": False,
            "notes": "Livro 1 integral ('Admoestações Úteis à Vida Espiritual') da Imitação de Cristo. Edição original em Domínio Público. Dataset editorial NEUU sob CC BY 4.0."
        },
        "lawrence-practice.json": {
            "src": neuu_dir / "lawrence" / "practice.json",
            "completeness": "full",
            "text_type": "translation",
            "translation_method": "claude-opus-4-6 (NEUU classics dataset)",
            "license": "CC-BY-4.0",
            "provenance_url": "https://github.com/neuu-org/bible-classics-dataset",
            "human_reviewed": False,
            "notes": "Conversações e cartas do Irmão Lawrence. Edição original de 1692 em Domínio Público. Dataset editorial NEUU sob CC BY 4.0."
        },
    }

    for dst_name, cfg in neuu_configs.items():
        src = cfg["src"]
        dst = target_theology_dir / dst_name
        if src.exists():
            with open(src, "r", encoding="utf-8") as f:
                content = json.load(f)
            meta = content.setdefault("metadata", {})
            meta["license"] = cfg["license"]
            meta["completeness"] = cfg["completeness"]
            meta["text_type"] = cfg["text_type"]
            meta["translation_method"] = cfg["translation_method"]
            meta["provenance_url"] = cfg["provenance_url"]
            meta["human_reviewed"] = cfg["human_reviewed"]
            meta["editorial_notes"] = cfg["notes"]
            with open(dst, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            print(f"[PROCESSADO] {src.name} -> {dst.relative_to(root)}")
        else:
            print(f"[ALERTA] Fonte não encontrada: {src}")

    # 2. Criar Jonathan Edwards (1741) — Pecadores nas Mãos de um Deus Irado (Extrato / Paráfrase Doutrinária)
    edwards_data = {
        "metadata": {
            "canonical_id": "edwards:sinners-in-the-hands-of-an-angry-god",
            "title": "Pecadores nas Mãos de um Deus Irado (Extrato Selecionado)",
            "title_en": "Sinners in the Hands of an Angry God (Selected Excerpt)",
            "author_full": "Jonathan Edwards",
            "author_short": "Jonathan Edwards",
            "author_pt": "Jonathan Edwards",
            "year": 1741,
            "language": "pt",
            "rights": "CC-BY-4.0 (Paráfrase/Seleção); Edição original de 1741 em Domínio Público universal",
            "license": "CC-BY-4.0",
            "completeness": "excerpt",
            "text_type": "paraphrase",
            "translation_method": "experimental-synthesis",
            "tradition": "Puritana Reformada",
            "subjects": ["Teologia Reformada", "Soteriologia", "Homilética Puritana", "Primeiro Grande Despertar"],
            "source_edition": "Edição original histórica publicada em Boston por S. Kneeland e T. Green (1741, Domínio Público universal); Gutenberg eBook #34632",
            "provenance_url": "https://www.gutenberg.org/ebooks/34632",
            "human_reviewed": False,
            "editorial_notes": "Extrato e seleção condensada em português (20 parágrafos doutrinários representativos) do sermão histórico proferido em 1741 sobre Dt 32:35. Não constitui tradução integral nem substitui a edição de referência em Domínio Público universal (Gutenberg #34632). Licenciado sob CC BY 4.0 para pesquisa."
        },
        "chapters": [
            {
                "number": 1,
                "title": "Texto Bíblico e Fundamento Doutrinário",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "'A seu tempo, quando resvalar o seu pé.' — Deuteronômio 32:35. Neste versículo, a vingança de Deus é ameaçada contra os israelitas ímpios e incrédulos, que pertenciam ao povo visível de Deus e viviam sob os meios da graça, mas que, não obstante todas as maravilhosas obras de Deus em favor deles, permaneceram desprovidos de juízo e discernimento espiritual."
                    },
                    {
                        "id": "p2",
                        "text": "A expressão 'quando resvalar o seu pé' implica as seguintes verdades sobre a punição e destruição a que esses israelitas culpados estavam expostos: primeiro, que estavam sempre expostos à destruição, como alguém que anda ou permanece em lugares escorregadios está sempre propenso a cair. A maneira de sua destruição é aqui aludida pelo tropeço e escorregão de seus pés."
                    },
                    {
                        "id": "p3",
                        "text": "Segundo, implica que estavam sempre expostos a uma destruição súbita e inesperada. Aquele que caminha em lugares escorregadios não pode prever em que instante cairá; quando cai, tomba sem aviso prévio. Terceiro, implica que estão sujeitos a cair por si mesmos, sem precisarem ser empurrados ou derrubados por mãos alheias, bastando apenas o seu próprio peso sobre terreno instável."
                    },
                    {
                        "id": "p4",
                        "text": "Quarto, a razão pela qual ainda não caíram reside unicamente no fato de que o tempo determinado por Deus ainda não chegou. Pois está dito: 'a seu tempo, o seu pé resvalará'. Então serão entregues à queda inevitável a que seu próprio peso continuamente os inclina. Deus não os sustentará mais nesses lugares escorregadios, mas os deixará cair."
                    },
                    {
                        "id": "p5",
                        "text": "A proposição central que pretendo insistir a partir destas palavras é esta: Não há nada, a não ser o mero e soberano beneplácito de Deus, que segure os homens ímpios fora do inferno por um único momento. Por beneplácito soberano entendo a Sua soberana vontade, livre de qualquer obrigação ou restrição externa."
                    }
                ]
            },
            {
                "number": 2,
                "title": "Dez Considerações Doutrinárias da Justiça e Soberania Divina",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "1. Não falta poder a Deus para lançar os homens ímpios no inferno a qualquer momento. As mãos dos homens não podem ser fortes quando Deus se levanta. O mais forte deles não tem poder para resistir a Ele, nem pode se livrar de Suas mãos. Ele não apenas é capaz de lançar homens ímpios no inferno, mas pode fazê-lo com a maior facilidade."
                    },
                    {
                        "id": "p2",
                        "text": "2. Eles merecem ser lançados no inferno; de modo que a justiça divina nunca se interpõe no caminho, nem faz qualquer objeção contra o uso do poder de Deus para destruí-los a qualquer momento. Pelo contrário, a justiça clama em alta voz por uma punição infinita para os seus pecados."
                    },
                    {
                        "id": "p3",
                        "text": "3. Eles já estão sob a sentença de condenação ao inferno. Não apenas merecem com justiça ser lançados ali, mas a sentença da lei de Deus, aquela regra imutável de justiça que Ele estabeleceu entre Si e a humanidade, já foi proferida contra eles: 'Aquele que não crê já está condenado' (João 3:18)."
                    },
                    {
                        "id": "p4",
                        "text": "4. Eles são agora os objetos daquela mesma ira e furor de Deus que é expressa nos tormentos do inferno. E a razão pela qual não descem ao inferno a cada minuto não é porque o Deus sob cujo poder estão não esteja sumamente irado com eles, assim como está com as muitas criaturas miseráveis agora atormentadas no inferno."
                    },
                    {
                        "id": "p5",
                        "text": "5. O diabo está pronto para cair sobre eles e tomá-los como seus, no instante exato em que Deus permitir. Eles pertencem a ele; suas almas estão sob a posse dele e debaixo de seu domínio. Os demônios os vigiam como leões famintos e vorazes que veem sua presa, mas são contidos pela mão de Deus."
                    },
                    {
                        "id": "p6",
                        "text": "6. Na alma dos homens ímpios reinam princípios infernais que já estariam acesos e arderiam no inferno, se não fossem as restrições impostas por Deus. Há na própria natureza dos homens carnais um fundamento estabelecido para os tormentos do inferno."
                    },
                    {
                        "id": "p7",
                        "text": "7. Não é segurança alguma para os homens ímpios, nem por um momento, o fato de não haverem sinais visíveis de morte iminente ao seu redor. O homem não-regenerado caminha sobre o abismo do inferno sobre uma ponte apodrecida, na qual há incontáveis lugares frágeis demais para suportar o seu peso."
                    },
                    {
                        "id": "p8",
                        "text": "8. O cuidado e prudência natural dos homens para preservar sua própria vida não lhes oferece segurança por um instante sequer. A sabedoria humana não é salvaguarda contra a espada da justiça divina."
                    },
                    {
                        "id": "p9",
                        "text": "9. Todo o trabalho e esforço que os ímpios empregam para escapar do inferno, enquanto continuam a rejeitar a Cristo, de nada lhes aproveitam. Quase todo homem natural se lisonjeia pensando que escapará do inferno por sua própria religiosidade e boas intenções."
                    },
                    {
                        "id": "p10",
                        "text": "10. Deus não se colocou sob nenhuma obrigação, por nenhuma promessa, de manter qualquer homem natural fora do inferno por um momento sequer. Deus não fez nenhuma promessa de vida eterna, nem de qualquer libertação da morte eterna, a não ser aquelas contidas na aliança da graça, as promessas dadas em Cristo, nas quais todas as promessas são sim e amém."
                    }
                ]
            },
            {
                "number": 3,
                "title": "Aplicação Prática e Apelo ao Despertar Espiritual",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "O Deus que segura você sobre o abismo do inferno, muito semelhante a alguém que segura uma aranha ou algum inseto repugnante sobre o fogo, abomina você e está terrivelmente provocado; Sua ira contra você queima como fogo; Ele o vê como digno de nada além de ser lançado no fogo."
                    },
                    {
                        "id": "p2",
                        "text": "Ó pecador! Considere o perigo pavoroso em que você se encontra. É sobre uma fornalha de ira, sobre um abismo escancarado e sem fundo, cheio do fogo da ira, que você está suspenso, sustentado apenas pela mão de Deus, cuja ira está tão provocada contra você como contra muitos dos condenados no inferno."
                    },
                    {
                        "id": "p3",
                        "text": "Você se apega a um fio frágil, com as chamas da ira divina faiscando ao redor dele, prontas a cada momento para queimá-lo e consumi-lo; e você não tem interesse em nenhum Mediador, nada em que se segurar, nada de seu para respirar ou clamar, nada que você tenha feito, nada que possa fazer para induzir Deus a poupá-lo por um único instante."
                    },
                    {
                        "id": "p4",
                        "text": "E agora você tem uma oportunidade extraordinária, um dia em que Cristo abriu amplamente a porta da misericórdia e está de pé clamando e chamando em alta voz aos pobres pecadores; um dia em que muitos estão correndo para o reino de Deus. Muitos estão diariamente vindo do leste, oeste, norte e sul; muitos que estavam ultimamente na mesma miserável condição em que você está agora, encontram-se felizes, com seus corações cheios de amor por Aquele que os amou e lavou de seus pecados em Seu próprio sangue."
                    },
                    {
                        "id": "p5",
                        "text": "Portanto, que todo aquele que está fora de Cristo agora desperte e fuja da ira vindoura. A ira do Deus Todo-Poderoso paira indubitavelmente sobre uma grande parte desta congregação. Que cada um fuja de Sodoma: 'Livra-te, salva a tua vida, não olhes para trás, nem pares em toda a planície; escapa-te para o monte, para que não pereças'."
                    }
                ]
            }
        ]
    }

    with open(target_theology_dir / "edwards-sinners-angry-god.json", "w", encoding="utf-8") as f:
        json.dump(edwards_data, f, indent=2, ensure_ascii=False)
    print(f"[CRIADO] edwards-sinners-angry-god.json em {target_theology_dir.relative_to(root)}")

    # 3. Criar Martinho Lutero (1529) — O Catecismo Menor (Seleção e Paráfrase Doutrinária)
    luther_data = {
        "metadata": {
            "canonical_id": "luther:small-catechism",
            "title": "O Catecismo Menor (Seleção Doutrinária)",
            "title_en": "The Small Catechism (Selected Doctrinal Summary)",
            "title_de": "Der Kleine Katechismus",
            "author_full": "Martinho Lutero",
            "author_short": "Martinho Lutero",
            "author_pt": "Martinho Lutero",
            "year": 1529,
            "language": "pt",
            "rights": "CC-BY-4.0 (Paráfrase/Seleção); Edição original histórica de 1529 em Domínio Público universal",
            "license": "CC-BY-4.0",
            "completeness": "excerpt",
            "text_type": "paraphrase",
            "translation_method": "experimental-synthesis",
            "tradition": "Luterana Magistral",
            "subjects": ["Teologia Luterana", "Catequese Clássica", "Doutrina Cristã", "Reforma Protestante"],
            "source_edition": "Wittenberg (1529); Livro de Concórdia (1580, Domínio Público universal); Gutenberg eBook #16012",
            "provenance_url": "https://www.gutenberg.org/ebooks/16012",
            "human_reviewed": False,
            "editorial_notes": "Seleção e paráfrase doutrinária condensada em português (31 seções essenciais: Decálogo, Credo, Pai Nosso, Sacramentos) do Catecismo Menor de 1529. Não substitui o texto integral do Livro de Concórdia de 1580 em Domínio Público. Licenciado sob CC BY 4.0 para pesquisa."
        },
        "chapters": [
            {
                "number": 1,
                "title": "Os Dez Mandamentos de Deus",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "Primeiro Mandamento: 'Não terás outros deuses diante de mim.' O que significa isto? Resposta: Devemos temer e amar a Deus sobre todas as coisas e confiar Nele de todo o coração."
                    },
                    {
                        "id": "p2",
                        "text": "Segundo Mandamento: 'Não tomarás o nome do Senhor teu Deus em vão.' O que significa isto? Resposta: Devemos temer e amar a Deus, para que não usemos Seu nome para amaldiçoar, jurar falso, praticar feitiçaria, mentir ou enganar, mas sim O invoquemos em todas as necessidades, oremos, louvemos e demos graças."
                    },
                    {
                        "id": "p3",
                        "text": "Terceiro Mandamento: 'Lembra-te do dia de sábado, para o santificar.' O que significa isto? Resposta: Devemos temer e amar a Deus, para que não desprezemos a pregação e a Sua Palavra, mas a consideremos santa, a ouçamos de bom grado e a guardemos no coração."
                    },
                    {
                        "id": "p4",
                        "text": "Quarto Mandamento: 'Honra a teu pai e a tua mãe.' O que significa isto? Resposta: Devemos temer e amar a Deus, para que não desprezemos nem irritemos nossos pais e superiores, mas lhes dediquemos respeito, os sirvamos, lhes obedeçamos, os amemos e tenhamos em alta estima."
                    },
                    {
                        "id": "p5",
                        "text": "Quinto Mandamento: 'Não matarás.' O que significa isto? Resposta: Devemos temer e amar a Deus, para que não causemos dano ou sofrimento ao nosso próximo em seu corpo, mas sim o ajudemos e o socorramos em todas as necessidades corporais."
                    },
                    {
                        "id": "p6",
                        "text": "Sexto Mandamento: 'Não adulterarás.' O que significa isto? Resposta: Devemos temer e amar a Deus, para que levemos uma vida pura e casta em palavras e ações, e cada um ame e honre seu cônjuge no matrimônio."
                    },
                    {
                        "id": "p7",
                        "text": "Sétimo Mandamento: 'Não furtarás.' O que significa isto? Resposta: Devemos temer e amar a Deus, para que não tomemos o dinheiro ou os bens de nosso próximo, nem os obtenhamos com mercadoria falsificada ou negócios desonestos, mas o ajudemos a melhorar e proteger seus bens e seu sustento."
                    },
                    {
                        "id": "p8",
                        "text": "Oitavo Mandamento: 'Não dirás falso testemunho contra o teu próximo.' O que significa isto? Resposta: Devemos temer e amar a Deus, para que não mintamos contra nosso próximo, não o traiamos, não o difamemos nem prejudiquemos sua reputação, mas o defendamos, falemos bem dele e interpretemos tudo da melhor maneira."
                    },
                    {
                        "id": "p9",
                        "text": "Nono Mandamento: 'Não cobiçarás a casa do teu próximo.' O que significa isto? Resposta: Devemos temer e amar a Deus, para que não tramemos contra a herança ou casa de nosso próximo, nem a obtenhamos sob aparência de direito legítimo, mas o sirvamos para que a conserve."
                    },
                    {
                        "id": "p10",
                        "text": "Décimo Mandamento: 'Não cobiçarás a mulher do teu próximo, nem os seus servos, nem as suas servas, nem coisa alguma que lhe pertença.' O que significa isto? Resposta: Devemos temer e amar a Deus, para que não afastemos nem seduzamos o cônjuge, os servos ou o gado de nosso próximo, mas os exortemos a permanecer e cumprir com dedicação seus deveres."
                    }
                ]
            },
            {
                "number": 2,
                "title": "O Credo Apostólico",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "Primeiro Artigo: Da Criação. 'Creio em Deus Pai Todo-Poderoso, Criador do céu e da terra.' O que significa isto? Resposta: Creio que Deus me criou juntamente com todas as criaturas, deu-me corpo e alma, olhos, ouvidos e todos os membros, razão e todos os sentidos, e ainda os preserva. Concede-me vestimentas e sapatos, comida e bebida, casa e lar, cônjuge e filhos, campos, gado e todos os bens; supre diária e abundantemente todas as necessidades deste corpo e vida. Guarda-me contra todo perigo e me protege de todo mal. Tudo isso faz unicamente por paterna e divina bondade e misericórdia, sem nenhum mérito ou dignidade de minha parte. Por tudo isso devo agradecer-Lhe, louvá-Lo, servi-Lo e obedecer-Lhe. Isto é certamente a verdade."
                    },
                    {
                        "id": "p2",
                        "text": "Segundo Artigo: Da Redenção. 'E em Jesus Cristo, Seu único Filho, nosso Senhor, o qual foi concebido por obra do Espírito Santo, nasceu da virgem Maria, padeceu sob o poder de Pôncio Pilatos, foi crucificado, morto e sepultado; desceu ao inferno; no terceiro dia ressuscitou dos mortos; subiu ao céu e está assentado à mão direita de Deus Pai Todo-Poderoso, donde há de vir a julgar os vivos e os mortos.' O que significa isto? Resposta: Creio que Jesus Cristo, verdadeiro Deus, gerado do Pai desde a eternidade, e também verdadeiro homem, nascido da virgem Maria, é meu Senhor. Ele me redimiu a mim, homem perdido e condenado, e me resgatou de todos os pecados, da morte e do poder do diabo, não com ouro ou prata, mas com Seu santo e precioso sangue e com Sua inocente paixão e morte, para que eu Lhe pertença, viva sob Seu reino e O sirva em eterna justiça, inocência e bem-aventurança, assim como Ele ressuscitou dos mortos, vive e reina eternamente. Isto é certamente a verdade."
                    },
                    {
                        "id": "p3",
                        "text": "Terceiro Artigo: Da Santificação. 'Creio no Espírito Santo, na santa Igreja cristã, na comunhão dos santos, na remissão dos pecados, na ressurreição da carne e na vida eterna. Amém.' O que significa isto? Resposta: Creio que por minha própria razão ou forças não posso crer em Jesus Cristo, meu Senhor, nem chegar a Ele; mas o Espírito Santo me chamou pelo Evangelho, iluminou-me com Seus dons, santificou-me e preservou-me na verdadeira fé. Do mesmo modo Ele chama, reúne, ilumina e santifica toda a Igreja cristã na terra e a preserva em Jesus Cristo na única e verdadeira fé. Nesta Igreja cristã Ele perdoa diária e plenamente todos os pecados a mim e a todos os crentes, e no último dia ressuscitará a mim e a todos os mortos, e dará a vida eterna a mim e a todos os crentes em Cristo. Isto é certamente a verdade."
                    }
                ]
            },
            {
                "number": 3,
                "title": "A Oração do Senhor (O Pai Nosso)",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "Introdução: 'Pai nosso que estás nos céus.' O que significa isto? Resposta: Deus quer nos encorajar cordialmente a crer que Ele é nosso verdadeiro Pai e nós somos Seus verdadeiros filhos, para que Lhe peçamos com toda a coragem e confiança, como filhos queridos pedem a seu querido pai."
                    },
                    {
                        "id": "p2",
                        "text": "Primeira Petição: 'Santificado seja o Teu nome.' O que significa isto? Resposta: O nome de Deus é certamente santo em si mesmo; mas pedimos nesta oração que ele seja santificado também entre nós. Isto acontece quando a Palavra de Deus é ensinada com pureza e retidão, e nós, como filhos de Deus, vivemos santamente de acordo com ela."
                    },
                    {
                        "id": "p3",
                        "text": "Segunda Petição: 'Venha o Teu reino.' O que significa isto? Resposta: O reino de Deus vem por si mesmo, sem a nossa oração; mas pedimos nesta oração que ele venha também a nós. Isto acontece quando nosso Pai celestial nos dá o Seu Espírito Santo, de modo que por Sua graça cremos em Sua santa Palavra e levamos uma vida piedosa aqui no tempo e acolá na eternidade."
                    },
                    {
                        "id": "p4",
                        "text": "Terceira Petição: 'Seja feita a Tua vontade, assim na terra como no céu.' O que significa isto? Resposta: A boa e graciosa vontade de Deus é feita sem a nossa oração; mas pedimos nesta oração que ela se faça também entre nós. Isto acontece quando Deus quebra e impede todo mau desígnio e vontade que não nos deixam santificar o nome de Deus nem deixam vir o Seu reino, tais como a vontade do diabo, do mundo e de nossa própria carne; e quando nos fortalece e conserva firmes em Sua Palavra e na fé até o fim."
                    },
                    {
                        "id": "p5",
                        "text": "Quarta Petição: 'O pão nosso de cada dia nos dá hoje.' O que significa isto? Resposta: Deus dá o pão de cada dia sem o nosso pedido, mesmo a todos os homens maus; mas pedimos nesta oração que nos faça reconhecer isso e receber o nosso pão de cada dia com ações de graças."
                    },
                    {
                        "id": "p6",
                        "text": "Quinta Petição: 'E perdoa-nos as nossas dívidas, assim como nós perdoamos aos nossos devedores.' O que significa isto? Resposta: Pedimos nesta oração que nosso Pai celeste não olhe para os nossos pecados, nem por causa deles nos negue o pedido, pois não somos dignos de nenhuma das coisas que pedimos, nem as merecemos; mas que no-las queira dar todas por graça, pois pecamos diariamente muito e merecemos apenas castigo. Assim também nós, por nossa vez, queremos cordialmente perdoar e de bom grado fazer o bem aos que pecam contra nós."
                    },
                    {
                        "id": "p7",
                        "text": "Sexta Petição: 'E não nos deixes cair em tentação.' O que significa isto? Resposta: Deus não tenta a ninguém; mas pedimos nesta oração que Deus queira nos proteger e guardar, para que o diabo, o mundo e a nossa própria carne não nos enganem nem nos seduzam para a falsa fé, desespero e outras grandes vergonhas e vícios; e que, mesmo sendo tentados, finalmente vençamos e obtenhamos a vitória."
                    },
                    {
                        "id": "p8",
                        "text": "Sétima Petição: 'Mas livra-nos do mal.' O que significa isto? Resposta: Pedimos nesta oração, como resumo de tudo, que nosso Pai celeste nos livre de todo mal do corpo e da alma, dos bens e da honra, e finalmente, quando chegar a nossa hora derradeira, nos conceda um fim bem-aventurado e nos recolha graciosamente deste vale de lágrimas para Si no céu."
                    },
                    {
                        "id": "p9",
                        "text": "Conclusão: 'Pois Teu é o reino, o poder e a glória para sempre. Amém.' O que significa Amém? Resposta: Significa que devo ter a certeza de que estes pedidos são aceitáveis ao Pai celeste e por Ele ouvidos; pois Ele próprio nos mandou orar assim e prometeu que nos ouvirá. Amém, amém, isto quer dizer: sim, sim, assim deve ser."
                    }
                ]
            },
            {
                "number": 4,
                "title": "O Sacramento do Santo Batismo",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "Primeiro: O que é o Batismo? Resposta: O Batismo não é apenas água simples, mas é a água contida no mandamento de Deus e ligada à Palavra de Deus. Qual é essa Palavra de Deus? É a que nosso Senhor Jesus Cristo diz no último capítulo de Mateus: 'Ide e fazei discípulos de todas as nações, batizando-os em nome do Pai e do Filho e do Espírito Santo'."
                    },
                    {
                        "id": "p2",
                        "text": "Segundo: Que dons ou benefícios o Batismo confere? Resposta: Opera o perdão dos pecados, livra da morte e do diabo e dá a salvação eterna a todos os que creem no que dizem as palavras e promessas de Deus. Quais são essas palavras e promessas de Deus? São as que nosso Senhor Jesus Cristo diz no último capítulo de Marcos: 'Quem crer e for batizado será salvo; mas quem não crer será condenado'."
                    },
                    {
                        "id": "p3",
                        "text": "Terceiro: Como pode a água fazer tão grandes coisas? Resposta: Não é a água certamente que as faz, mas a Palavra de Deus que está com e junto à água, e a fé que confia nessa Palavra de Deus ligada à água. Pois sem a Palavra de Deus a água é simples água e nenhum Batismo; mas com a Palavra de Deus é um Batismo, isto é, uma água graciosa da vida e um banho de novo nascimento no Espírito Santo."
                    },
                    {
                        "id": "p4",
                        "text": "Quarto: O que significa esse batizar com água? Resposta: Significa que o velho Adão em nós deve ser afogado por diária contrição e arrependimento, e morrer com todos os pecados e maus desejos; e, por outro lado, deve surgir e ressuscitar diariamente um novo homem, que viva eternamente em justiça e pureza diante de Deus."
                    }
                ]
            },
            {
                "number": 5,
                "title": "O Sacramento do Altar (A Ceia do Senhor)",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "O que é o Sacramento do Altar? Resposta: É o verdadeiro corpo e sangue de nosso Senhor Jesus Cristo, sob o pão e o vinho, instituído por Cristo mesmo para nós, cristãos, comermos e bebermos."
                    },
                    {
                        "id": "p2",
                        "text": "Onde está escrito isto? Resposta: Assim escrevem os santos evangelistas Mateus, Marcos, Lucas e o apóstolo Paulo: 'Nosso Senhor Jesus Cristo, na noite em que foi traído, tomou o pão e, havendo dado graças, o partiu e deu a Seus discípulos, dizendo: Tomai, comei; isto é o Meu corpo que é dado por vós; fazei isto em memória de Mim. Do mesmo modo tomou também o cálice, depois da ceia, e, havendo dado graças, o deu a eles, dizendo: Bebei dele todos; este cálice é o Novo Testamento no Meu sangue, que é derramado por vós para remissão dos pecados; fazei isto, todas as vezes que o beberdes, em memória de Mim'."
                    },
                    {
                        "id": "p3",
                        "text": "Que proveito há em comer e beber assim? Resposta: Isto nos mostram estas palavras: 'Dado e derramado por vós para remissão dos pecados'; a saber: que na Ceia nos é concedido o perdão dos pecados, vida e salvação por meio destas palavras. Pois onde há remissão dos pecados, aí há também vida e salvação."
                    },
                    {
                        "id": "p4",
                        "text": "Como pode o comer e beber corporal fazer tão grandes coisas? Resposta: Não é o comer e beber certamente que as faz, mas aquelas palavras que ali estão: 'Dado e derramado por vós para remissão dos pecados'. Estas palavras, juntamente com o comer e beber corporal, são o elemento principal no sacramento; e quem crê nestas palavras tem o que elas dizem e expressam, a saber: o perdão dos pecados."
                    },
                    {
                        "id": "p5",
                        "text": "Quem, pois, recebe este sacramento dignamente? Resposta: O jejuar e preparar-se corporalmente é certamente uma boa disciplina exterior; mas verdadeiramente digno e bem preparado está aquele que tem fé nestas palavras: 'Dado e derramado por vós para remissão dos pecados'. Mas quem não crê nestas palavras ou delas duvida é indigno e desqualificado; pois a palavra 'por vós' exige corações verdadeiramente crentes."
                    }
                ]
            }
        ]
    }

    with open(target_theology_dir / "luther-small-catechism.json", "w", encoding="utf-8") as f:
        json.dump(luther_data, f, indent=2, ensure_ascii=False)
    print(f"[CRIADO] luther-small-catechism.json em {target_theology_dir.relative_to(root)}")

    # 4. Criar Os Trinta e Nove Artigos de Religião (1571) — Extrato Selecionado Doutrinário
    articles_data = {
        "metadata": {
            "canonical_id": "anglican:thirty-nine-articles",
            "title": "Os Trinta e Nove Artigos de Religião (Seleção Doutrinária)",
            "title_en": "The Thirty-Nine Articles of Religion (Selected Articles)",
            "author_full": "Convocação de Cantuária e Bispos da Igreja da Inglaterra",
            "author_short": "Convocação Anglicana",
            "author_pt": "Igreja da Inglaterra (1571)",
            "year": 1571,
            "language": "pt",
            "rights": "CC-BY-4.0 (Paráfrase/Seleção); Edição histórica original de 1571 em Domínio Público universal",
            "license": "CC-BY-4.0",
            "completeness": "excerpt",
            "text_type": "paraphrase",
            "translation_method": "experimental-synthesis",
            "tradition": "Anglicana Reformada",
            "subjects": ["Confissões de Fé", "Teologia Reformada", "Anglicanismo Histórico", "Doutrina Protestante"],
            "source_edition": "Book of Common Prayer (1571/1662, Domínio Público universal)",
            "provenance_url": "https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/book-common-prayer/articles-religion",
            "human_reviewed": False,
            "editorial_notes": "Seleção e extrato em português de 19 artigos representativos dos 39 Artigos da Igreja da Inglaterra (1571). Não contém a totalidade dos 39 artigos originais. Licenciado sob CC BY 4.0 para pesquisa."
        },
        "chapters": [
            {
                "number": 1,
                "title": "Artigos I a V — Da Fé na Santíssima Trindade e da Encarnação do Verbo",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "Artigo I — Da Fé na Santíssima Trindade: Há um único Deus vivo e verdadeiro, eterno, sem corpo, partes ou paixões; de poder, sabedoria e bondade infinitos; Criador e Conservador de todas as coisas visíveis e invisíveis. E na unidade desta Divindade há três Pessoas de uma só substância, poder e eternidade: o Pai, o Filho e o Espírito Santo."
                    },
                    {
                        "id": "p2",
                        "text": "Artigo II — Do Verbo ou Filho de Deus que Se fez verdadeiro Homem: O Filho, que é o Verbo do Pai, gerado da eternidade do Pai, verdadeiro e eterno Deus, de uma só substância com o Pai, tomou a natureza humana no ventre da bendita Virgem, da substância dela; de modo que duas naturezas inteiras e perfeitas, a saber, a Divina e a Humana, se uniram em uma só Pessoa, para jamais serem divididas, das quais é um só Cristo, verdadeiro Deus e verdadeiro Homem; que verdadeiramente padeceu, foi crucificado, morto e sepultado, para reconciliar Seu Pai conosco, e ser um sacrifício, não apenas pela culpa original, mas também por todos os pecados atuais dos homens."
                    },
                    {
                        "id": "p3",
                        "text": "Artigo III — Da Descida de Cristo ao Inferno: Assim como Cristo morreu por nós e foi sepultado, também deve ser crido que Ele desceu ao inferno."
                    },
                    {
                        "id": "p4",
                        "text": "Artigo IV — Da Ressurreição de Cristo: Cristo verdadeiramente ressuscitou dos mortos, e tomou novamente Seu corpo, com carne, ossos e tudo o que pertence à integridade da natureza humana; com o qual Ele subiu ao céu, e ali está assentado até que volte para julgar todos os homens no último dia."
                    },
                    {
                        "id": "p5",
                        "text": "Artigo V — Do Espírito Santo: O Espírito Santo, procedente do Pai e do Filho, é de uma só substância, majestade e glória com o Pai e o Filho, verdadeiro e eterno Deus."
                    }
                ]
            },
            {
                "number": 2,
                "title": "Artigos VI a VIII — Da Suficiência da Escritura e dos Credos",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "Artigo VI — Da Suficiência das Sagradas Escrituras para a Salvação: A Sagrada Escritura contém todas as coisas necessárias para a salvação; de modo que tudo o que nela não se lê, nem por ela se pode provar, não deve ser exigido de homem algum para ser crido como artigo de fé, ou considerado necessário para a salvação. Pelo nome de Sagrada Escritura entendemos aqueles livros canônicos do Antigo e do Novo Testamento, de cuja autoridade nunca houve dúvida na Igreja."
                    },
                    {
                        "id": "p2",
                        "text": "Artigo VII — Do Antigo Testamento: O Antigo Testamento não é contrário ao Novo; pois tanto no Antigo como no Novo a vida eterna é oferecida ao gênero humano por Cristo, que é o único Mediador entre Deus e o homem, sendo Ele Deus e Homem. Portanto, não devem ser ouvidos aqueles que fingem que os antigos patriarcas esperavam apenas promessas transitórias."
                    },
                    {
                        "id": "p3",
                        "text": "Artigo VIII — Dos Três Credos: Os Três Credos — o Niceno, o de Atanásio e o que vulgarmente se chama Credo dos Apóstolos — devem ser inteiramente recebidos e cridos; pois podem ser provados por testemunhos evidentes da Sagrada Escritura."
                    }
                ]
            },
            {
                "number": 3,
                "title": "Artigos IX a XVIII — Da Graça, Pecado Original, Justificação e Eleição",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "Artigo IX — Do Pecado Original ou de Nascimento: O pecado original não consiste na imitação de Adão (como os pelagianos falsamente dizem), mas é a falta e corrupção da natureza de todo homem gerado naturalmente da estirpe de Adão; pelo qual o homem está muito longe da justiça original e é de sua própria natureza inclinado para o mal, de modo que a carne cobiça sempre contra o espírito; e, portanto, em toda pessoa nascida neste mundo, merece a ira e a condenação de Deus."
                    },
                    {
                        "id": "p2",
                        "text": "Artigo X — Do Livre-Arbítrio: A condição do homem após a queda de Adão é tal que ele não pode se converter e se preparar, por sua própria força natural e boas obras, para a fé e invocação a Deus. Portanto, não temos poder para fazer boas obras agradáveis e aceitáveis a Deus, sem que a graça de Deus por Cristo nos preceda, para que tenhamos boa vontade, e coopere conosco quando temos essa boa vontade."
                    },
                    {
                        "id": "p3",
                        "text": "Artigo XI — Da Justificação do Homem: Somos tidos por justos diante de Deus somente pelo mérito de nosso Senhor e Salvador Jesus Cristo, pela fé, e não pelas nossas próprias obras ou merecimentos. Portanto, que somos justificados somente pela fé é uma doutrina mui salutar e cheia de consolo, como mais amplamente é expresso na Homilia da Justificação."
                    },
                    {
                        "id": "p4",
                        "text": "Artigo XII — Das Boas Obras: Posto que as boas obras, que são os frutos da fé e seguem a justificação, não podem expiar os nossos pecados, nem suportar a severidade do juízo de Deus, contudo são agradáveis e aceitáveis a Deus em Cristo, e brotam necessariamente de uma fé verdadeira e viva; de modo que por elas uma fé viva pode ser tão evidentemente conhecida como a árvore se conhece pelo seu fruto."
                    },
                    {
                        "id": "p5",
                        "text": "Artigo XVII — Da Predestinação e Eleição: A predestinação para a vida é o propósito eterno de Deus, pelo qual (antes de lançados os fundamentos do mundo) Ele decretou firmemente por Seu conselho, secreto a nós, livrar da maldição e condenação aqueles que escolheu em Cristo dentre o gênero humano, e conduzi-los por Cristo à salvação eterna, como vasos feitos para honra. Pelo que, aqueles que são agraciados com tão excelente benefício de Deus são chamados segundo o propósito de Deus pelo Seu Espírito operando no devido tempo; eles pela graça obedecem ao chamamento; são justificados livremente; são feitos filhos de Deus por adoção; são conformados à imagem de Seu Filho unigênito Jesus Cristo; andam religiosamente em boas obras; e finalmente, pela misericórdia de Deus, alcançam a bem-aventurança eterna."
                    },
                    {
                        "id": "p6",
                        "text": "Artigo XVIII — De Obter a Salvação Eterna Apenas pelo Nome de Cristo: Devem ser anatemizados aqueles que presumem dizer que todo homem será salvo pela lei ou seita que professa, contanto que seja diligente em enquadrar sua vida segundo essa lei e a luz da natureza. Pois a Sagrada Escritura nos propõe apenas o nome de Jesus Cristo pelo qual os homens devem ser salvos."
                    }
                ]
            },
            {
                "number": 4,
                "title": "Artigos XIX a XXXIX — Da Igreja, dos Sacramentos e da Ordem Civil",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "Artigo XIX — Da Igreja: A Igreja visível de Cristo é uma congregação de fiéis, na qual a pura Palavra de Deus é pregada e os Sacramentos são devidamente ministrados segundo a ordenança de Cristo em todas as coisas que necessariamente são requeridas para os mesmos."
                    },
                    {
                        "id": "p2",
                        "text": "Artigo XXV — Dos Sacramentos: Os Sacramentos instituídos por Cristo não são apenas insígnias ou testemunhos da profissão dos cristãos, mas antes testemunhos certos e sinais eficazes da graça e da boa vontade de Deus para conosco, pelos quais Ele opera invisivelmente em nós, e não apenas desperta, mas também fortalece e confirma a nossa fé Nele. Há dois Sacramentos instituídos por Cristo nosso Senhor no Evangelho, a saber: o Batismo e a Ceia do Senhor."
                    },
                    {
                        "id": "p3",
                        "text": "Artigo XXVII — Do Batismo: O Batismo não é apenas um sinal de profissão e marca de distinção pela qual os cristãos se diferenciam dos não batizados, mas é também um sinal de regeneração ou novo nascimento, pelo qual, como por um instrumento, os que recebem o Batismo retamente são enxertados na Igreja; as promessas do perdão do pecado e de nossa adoção em filhos de Deus pelo Espírito Santo são visivelmente confirmadas; a fé é confirmada e a graça aumentada pela virtude da oração a Deus."
                    },
                    {
                        "id": "p4",
                        "text": "Artigo XXVIII — Da Ceia do Senhor: A Ceia do Senhor não é apenas um sinal do amor mútuo que os cristãos devem ter entre si, mas antes é um sacramento de nossa redenção pela morte de Cristo; de modo que, para aqueles que dignamente, com fé e com a devida preparação a recebem, o Pão que partimos é uma comunhão do Corpo de Cristo, e semelhantemente o Cálice da bênção é uma comunhão do Sangue de Cristo. A transubstanciação (ou a mudança da substância do pão e do vinho) na Ceia de nosso Senhor não pode ser provada pela Sagrada Escritura; antes é repugnante às palavras claras da Escritura, subverte a natureza de um Sacramento, e tem dado ocasião a muitas superstições."
                    },
                    {
                        "id": "p5",
                        "text": "Artigo XXXVII — Dos Magistrados Civis: O Magistrado Civil tem poder supremo sobre todas as ordens e estados civis, e a ele pertence reprimir os maus com a espada temporal e defender os que fazem o bem. As leis civis podem punir homens cristãos com a morte por crimes hediondos e graves, e é lícito aos homens cristãos, por ordem do magistrado, pegar em armas e servir nas guerras."
                    }
                ]
            }
        ]
    }

    with open(target_theology_dir / "thirty-nine-articles.json", "w", encoding="utf-8") as f:
        json.dump(articles_data, f, indent=2, ensure_ascii=False)
    print(f"[CRIADO] thirty-nine-articles.json em {target_theology_dir.relative_to(root)}")

    # 5. Criar A Confissão de Fé Batista de 1689 (2LCF) — Extrato Selecionado Doutrinário
    baptist_data = {
        "metadata": {
            "canonical_id": "baptist:confession-1689",
            "title": "A Confissão de Fé Batista de 1689 (Extrato de 4 Capítulos)",
            "title_en": "The 1689 London Baptist Confession of Faith (Selected Chapters)",
            "author_full": "Ministros e Mensageiros de Igrejas Batistas Particulares",
            "author_short": "Assembleia Batista de Londres (1689)",
            "author_pt": "Batistas Particulares (1689)",
            "year": 1689,
            "language": "pt",
            "rights": "CC-BY-4.0 (Paráfrase/Seleção); Edição original histórica de 1689 em Domínio Público universal",
            "license": "CC-BY-4.0",
            "completeness": "excerpt",
            "text_type": "paraphrase",
            "translation_method": "experimental-synthesis",
            "tradition": "Batista Particular Reformada",
            "subjects": ["Confissões de Fé", "Teologia Reformada Federal", "Batismo de Crentes", "Puritanismo Batista"],
            "source_edition": "Londres (1689, Domínio Público universal)",
            "provenance_url": "https://www.reformedreader.org/ccc/1689lbc/1689bcf.htm",
            "human_reviewed": False,
            "editorial_notes": "Extrato representativo condensado em português de 4 capítulos essenciais (Escritura, Trindade, Decreto/Salvação, Igreja/Sacramentos) dos 32 capítulos da Segunda Confissão Londrina de 1689. Não contém os 32 capítulos completos nem as referências bíblicas integrais. Licenciado sob CC BY 4.0 para pesquisa."
        },
        "chapters": [
            {
                "number": 1,
                "title": "Da Sagrada Escritura",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "1. A Santa Escritura é a única regra suficiente, correta e infalível de todo conhecimento, fé e obediência salvíficos. Embora a luz da natureza e as obras da criação e da providência manifestem a bondade, sabedoria e poder de Deus, a ponto de deixar os homens inescusáveis, contudo não são suficientes para dar aquele conhecimento de Deus e de Sua vontade que é necessário para a salvação."
                    },
                    {
                        "id": "p2",
                        "text": "2. Sob o título de Santa Escritura, ou a Palavra de Deus escrita, estão agora contidos todos os livros do Antigo e do Novo Testamento, a saber, trinta e nove livros do Antigo e vinte e sete do Novo, todos dados por inspiração de Deus para serem a regra de fé e vida."
                    },
                    {
                        "id": "p3",
                        "text": "3. A autoridade da Santa Escritura, pela qual ela deve ser crida, não depende do testemunho de qualquer homem ou igreja, mas inteiramente de Deus (que é a própria verdade), seu Autor; portanto, ela deve ser recebida porque é a Palavra de Deus."
                    },
                    {
                        "id": "p4",
                        "text": "4. Todo o conselho de Deus a respeito de todas as coisas necessárias para Sua própria glória, para a salvação, fé e vida do homem, está expressamente registrado na Escritura, ou pode ser lógica e necessariamente deduzido dela; à qual nada, em tempo algum, deve ser acrescentado, seja por novas revelações do Espírito, ou por tradições de homens."
                    }
                ]
            },
            {
                "number": 2,
                "title": "De Deus e da Santíssima Trindade",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "1. O Senhor nosso Deus é um único Deus vivo e verdadeiro; cuja subsistência está em Si mesmo e provém de Si mesmo; infinito em ser e perfeição; cuja essência não pode ser compreendida por ninguém a não ser por Si mesmo; espírito puríssimo, invisível, sem corpo, partes ou paixões; imutável, imenso, eterno, Todo-Poderoso, sumamente sábio, santo, livre e absoluto."
                    },
                    {
                        "id": "p2",
                        "text": "2. Nesta divina e infinita substância há três subsistências, o Pai, o Verbo ou Filho, e o Espírito Santo, de uma só substância, poder e eternidade, cada um tendo toda a essência divina, contudo a essência indivisa. O Pai não procede de ninguém, nem é gerado nem procedente; o Filho é eternamente gerado do Pai; o Espírito Santo eternamente procedente do Pai e do Filho; todos infinitos, sem princípio, sendo, portanto, um só Deus."
                    }
                ]
            },
            {
                "number": 3,
                "title": "Do Decreto de Deus e da Salvação em Cristo",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "1. Deus decretou em Si mesmo, desde toda a eternidade, pelo conselho sapientíssimo e santo de Sua própria vontade, livre e imutavelmente, todas as coisas que haviam de acontecer; contudo, de tal modo que nem Deus é o autor do pecado, nem tem comunhão com ele, nem violência é feita à vontade da criatura, nem a contingência das causas secundárias é tirada, antes estabelecida."
                    },
                    {
                        "id": "p2",
                        "text": "2. Aprouve a Deus, em Seu eterno propósito, escolher e ordenar o Senhor Jesus, Seu Filho unigênito, segundo a aliança feita entre ambos, para ser o Mediador entre Deus e o homem; o Profeta, Sacerdote e Rei; a Cabeça e Salvador de Sua Igreja; o Herdeiro de todas as coisas e o Juiz do mundo; a quem Ele, desde toda a eternidade, deu um povo para ser Sua semente, e para ser por Ele, no tempo, redimido, chamado, justificado, santificado e glorificado."
                    },
                    {
                        "id": "p3",
                        "text": "3. Aqueles a quem Deus eficazmente chama, Ele também justifica livremente; não por infundir justiça neles, mas por perdoar os seus pecados e por considerar e aceitar as suas pessoas como justas; não por qualquer coisa operada neles ou feita por eles, mas somente por amor de Cristo; não por imputar a fé mesma, o ato de crer, ou qualquer outra obediência evangélica a eles como justiça, mas por imputar a ativa obediência de Cristo a toda a lei e Sua passiva obediência na morte para a total e única justiça deles pela fé."
                    }
                ]
            },
            {
                "number": 4,
                "title": "Da Igreja e dos Sacramentos (Batismo e Ceia)",
                "paragraphs": [
                    {
                        "id": "p1",
                        "text": "1. A Igreja católica ou universal, que (com respeito à obra interna do Espírito e da verdade da graça) pode ser chamada invisível, consiste do número total dos eleitos que já foram, são ou ainda serão reunidos em um sob Cristo, sua Cabeça; e é a esposa, o corpo, a plenitude Daquele que enche tudo em todos."
                    },
                    {
                        "id": "p2",
                        "text": "2. O Batismo é uma ordenança do Novo Testamento, instituída por Jesus Cristo, para ser para aquele que é batizado um sinal de sua comunhão com Ele em Sua morte e ressurreição; de seu enxerto Nele; da remissão dos pecados; e de sua entrega a Deus por Jesus Cristo, para viver e andar em novidade de vida."
                    },
                    {
                        "id": "p3",
                        "text": "3. Aqueles que realmente professam arrependimento para com Deus e fé em nosso Senhor Jesus Cristo, e obediência a Ele, são os únicos sujeitos apropriados desta ordenança. O elemento exterior a ser usado nesta ordenança é a água, na qual a pessoa deve ser imersa em nome do Pai e do Filho e do Espírito Santo."
                    },
                    {
                        "id": "p4",
                        "text": "4. A Ceia do Senhor Jesus foi instituída por Ele na mesma noite em que foi traído, para ser observada em Suas igrejas até o fim do mundo, para perpétua lembrança e demonstração ao mundo do sacrifício de Si mesmo em Sua morte; confirmação da fé dos crentes em todos os benefícios dela, seu alimento espiritual e crescimento Nele, e para ser um vínculo e penhor de sua comunhão com Ele e uns com os outros."
                    }
                ]
            }
        ]
    }

    with open(target_theology_dir / "baptist-confession-1689.json", "w", encoding="utf-8") as f:
        json.dump(baptist_data, f, indent=2, ensure_ascii=False)
    print(f"[CRIADO] baptist-confession-1689.json em {target_theology_dir.relative_to(root)}")

    print("\n[CONCLUÍDO] Todos os 8 arquivos do acervo teológico aprovado estão prontos em corpus/approved/theology/")


if __name__ == "__main__":
    create_theology_corpus()
