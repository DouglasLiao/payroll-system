import {
  Box,
  Button,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Divider,
} from '@mui/material'
import { useNavigate } from 'react-router-dom'
import BoltIcon from '@mui/icons-material/Bolt'
import BusinessIcon from '@mui/icons-material/Business'
import NoteAltIcon from '@mui/icons-material/NoteAlt'
import EmailIcon from '@mui/icons-material/Email'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <Box
      sx={{
        bgcolor: 'background.default',
        color: 'text.primary',
        minHeight: '100vh',
      }}
    >
      {/* Navigation */}
      <Box
        component="nav"
        sx={{
          position: 'fixed',
          top: 0,
          width: '100%',
          zIndex: 100,
          bgcolor: 'background.paper',
          borderBottom: 1,
          borderColor: 'divider',
          py: 1.5,
          px: { xs: 2, md: 5 },
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: 28,
              height: 28,
              bgcolor: 'primary.main',
              borderRadius: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          />
          <Typography variant="h6" fontWeight={700}>
            Payroll
          </Typography>
        </Box>

        <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 4 }}>
          {[
            { label: 'Recursos', href: '#recursos' },
            { label: 'Como Funciona', href: '#fluxo' },
          ].map((item) => (
            <Typography
              key={item.label}
              component="a"
              href={item.href}
              sx={{
                color: 'text.secondary',
                textDecoration: 'none',
                fontWeight: 500,
                fontSize: '0.9rem',
                '&:hover': { color: 'primary.main' },
              }}
            >
              {item.label}
            </Typography>
          ))}
        </Box>

        <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
          <Button
            variant="text"
            onClick={() => navigate('/login')}
            sx={{ color: 'text.primary', fontWeight: 500 }}
          >
            Entrar
          </Button>
          <Button
            variant="contained"
            onClick={() => navigate('/register')}
            sx={{ fontWeight: 600, px: 2.5 }}
          >
            Solicitar Acesso
          </Button>
        </Box>
      </Box>

      {/* Hero Section */}
      <Box
        sx={{
          pt: { xs: 14, md: 18 },
          pb: { xs: 8, md: 12 },
          px: { xs: 2, md: 5 },
          bgcolor: 'background.paper',
          borderBottom: 1,
          borderColor: 'divider',
          textAlign: 'center',
        }}
      >
        <Container maxWidth="md">
          <Typography
            variant="h1"
            sx={{
              fontSize: { xs: '2.25rem', md: '3.25rem' },
              fontWeight: 700,
              lineHeight: 1.15,
              mb: 2.5,
              color: 'text.primary',
            }}
          >
            Folha de Pagamento PJ{' '}
            <Box component="span" sx={{ color: 'primary.main' }}>
              automatizada e sem erros
            </Box>
          </Typography>
          <Typography
            sx={{
              fontSize: '1.1rem',
              color: 'text.secondary',
              mb: 4,
              maxWidth: 560,
              mx: 'auto',
              lineHeight: 1.7,
            }}
          >
            Calcule pró-rata, vale transporte e horas extras com precisão.
            Gerencie múltiplas empresas e prestadores em uma única plataforma.
          </Typography>

          <Box
            sx={{
              display: 'flex',
              gap: 2,
              justifyContent: 'center',
              flexWrap: 'wrap',
            }}
          >
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/register')}
              sx={{ fontWeight: 600, px: 4, py: 1.25 }}
            >
              Solicitar Acesso Gratuito
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => {
                document
                  .getElementById('fluxo')
                  ?.scrollIntoView({ behavior: 'smooth' })
              }}
              sx={{ fontWeight: 600, px: 4, py: 1.25 }}
            >
              Ver como funciona
            </Button>
          </Box>

          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              gap: { xs: 3, md: 6 },
              mt: 6,
              pt: 4,
              borderTop: 1,
              borderColor: 'divider',
              flexWrap: 'wrap',
            }}
          >
            {[
              { value: '100%', label: 'Automatizado' },
              { value: 'Zero', label: 'Erros de Cálculo' },
              { value: 'Multi', label: 'Empresas em 1 conta' },
            ].map((stat) => (
              <Box key={stat.label} sx={{ textAlign: 'center' }}>
                <Typography
                  sx={{
                    fontSize: '1.75rem',
                    fontWeight: 700,
                    color: 'primary.main',
                    lineHeight: 1,
                  }}
                >
                  {stat.value}
                </Typography>
                <Typography
                  sx={{
                    fontSize: '0.8rem',
                    color: 'text.secondary',
                    mt: 0.5,
                    textTransform: 'uppercase',
                    letterSpacing: 0.5,
                  }}
                >
                  {stat.label}
                </Typography>
              </Box>
            ))}
          </Box>

          {/* Dashboard Preview Image */}
          <Box
            sx={{
              mt: 6,
              borderRadius: 2,
              overflow: 'hidden',
              border: 1,
              borderColor: 'divider',
              boxShadow: 3,
              maxWidth: 900,
              mx: 'auto',
            }}
          >
            <Box
              component="img"
              src="/dashboard-preview.png"
              alt="Preview do dashboard de folha de pagamento"
              sx={{ width: '100%', display: 'block' }}
            />
          </Box>
        </Container>
      </Box>

      {/* Features Section */}
      <Container
        id="recursos"
        sx={{ py: { xs: 8, md: 12 }, maxWidth: '1100px !important' }}
      >
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography
            variant="h2"
            sx={{
              fontSize: { xs: '1.75rem', md: '2.25rem' },
              fontWeight: 700,
              mb: 1.5,
            }}
          >
            Criado para escalar a sua operação
          </Typography>
          <Typography sx={{ color: 'text.secondary', fontSize: '1rem' }}>
            Tudo que você precisa em uma plataforma de gestão financeira B2B.
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {[
            {
              icon: <BoltIcon />,
              title: 'Motor de Cálculo Inteligente',
              desc: 'Calcula automaticamente pró-rata para admissões e demissões, horas extras e feriados locais via Workalendar.',
            },
            {
              icon: <BusinessIcon />,
              title: 'Multi-Tenancy',
              desc: 'Administre todos os CNPJs da sua empresa por meio de uma conta única com controle de permissões granular.',
            },
            {
              icon: <NoteAltIcon />,
              title: 'Math Templates',
              desc: 'Crie templates de cálculo reutilizáveis e aplique-os em massa a todos os colaboradores de uma empresa.',
            },
            {
              icon: <EmailIcon />,
              title: 'Disparo de Comprovantes',
              desc: 'Ao aprovar os pagamentos, o sistema gera recibos em PDF e notifica cada prestador automaticamente por e-mail.',
            },
          ].map((feat) => (
            <Grid size={{ xs: 12, sm: 6 }} key={feat.title}>
              <Card
                sx={{
                  height: '100%',
                  p: 1,
                }}
              >
                <CardContent>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: 1,
                      bgcolor: 'primary.main',
                      color: 'primary.contrastText',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                    }}
                  >
                    {feat.icon}
                  </Box>
                  <Typography
                    variant="h6"
                    sx={{ mb: 1, fontWeight: 600, fontSize: '1rem' }}
                  >
                    {feat.title}
                  </Typography>
                  <Typography
                    sx={{
                      color: 'text.secondary',
                      lineHeight: 1.65,
                      fontSize: '0.9rem',
                    }}
                  >
                    {feat.desc}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      <Divider />

      {/* Flow Section */}
      <Box
        id="fluxo"
        sx={{
          py: { xs: 8, md: 12 },
          bgcolor: 'background.paper',
        }}
      >
        <Container sx={{ maxWidth: '1100px !important' }}>
          <Grid container spacing={8} alignItems="flex-start">
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography
                variant="h2"
                sx={{ fontSize: '2rem', fontWeight: 700, mb: 1.5 }}
              >
                Fluxo claro e previsível
              </Typography>
              <Typography
                sx={{ color: 'text.secondary', mb: 5, fontSize: '1rem' }}
              >
                Do cadastro do prestador ao pagamento aprovado, cada etapa
                rastreada e auditável.
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3.5 }}>
                {[
                  {
                    num: 1,
                    title: 'Setup de Contrato',
                    desc: 'Defina honorários, vale transporte, regra de dias úteis e método de recebimento.',
                  },
                  {
                    num: 2,
                    title: 'Lançamento de Variáveis',
                    desc: 'Adicione horas extras, descontos ou faltas. Os cálculos são processados em tempo real.',
                  },
                  {
                    num: 3,
                    title: 'Aprovação e Pagamento',
                    desc: 'Revise os totais, aprove a folha e os comprovantes são enviados automaticamente.',
                  },
                ].map((step) => (
                  <Box
                    key={step.num}
                    sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}
                  >
                    <Box
                      sx={{
                        width: 32,
                        height: 32,
                        borderRadius: '50%',
                        bgcolor: 'primary.main',
                        color: 'primary.contrastText',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 700,
                        fontSize: '0.85rem',
                        flexShrink: 0,
                        mt: 0.25,
                      }}
                    >
                      {step.num}
                    </Box>
                    <Box>
                      <Typography
                        variant="subtitle1"
                        sx={{ fontWeight: 600, mb: 0.5 }}
                      >
                        {step.title}
                      </Typography>
                      <Typography
                        sx={{ color: 'text.secondary', fontSize: '0.9rem' }}
                      >
                        {step.desc}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <Card sx={{ p: 3 }}>
                <Typography
                  variant="subtitle2"
                  sx={{ mb: 3, color: 'text.secondary', fontWeight: 600 }}
                >
                  Resumo da Folha — Fevereiro 2026
                </Typography>

                {[
                  { label: 'Honorário Base', value: 'R$ 5.000,00' },
                  { label: 'Vale Transporte', value: 'R$ 220,00' },
                  { label: 'Horas Extras (8h)', value: 'R$ 375,00' },
                  { label: 'Desconto — Falta', value: '— R$ 166,67' },
                ].map((row) => (
                  <Box
                    key={row.label}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      py: 1.25,
                      borderBottom: 1,
                      borderColor: 'divider',
                    }}
                  >
                    <Typography
                      sx={{ color: 'text.secondary', fontSize: '0.9rem' }}
                    >
                      {row.label}
                    </Typography>
                    <Typography sx={{ fontWeight: 600, fontSize: '0.9rem' }}>
                      {row.value}
                    </Typography>
                  </Box>
                ))}

                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    pt: 2,
                    mt: 1,
                  }}
                >
                  <Typography sx={{ fontWeight: 700 }}>
                    Total Líquido
                  </Typography>
                  <Typography
                    sx={{
                      fontWeight: 700,
                      color: 'primary.main',
                      fontSize: '1.1rem',
                    }}
                  >
                    R$ 5.428,33
                  </Typography>
                </Box>

                <Box
                  sx={{
                    mt: 3,
                    p: 1.5,
                    bgcolor: 'action.hover',
                    borderRadius: 1,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                  }}
                >
                  <CheckCircleOutlineIcon
                    sx={{ color: 'success.main', fontSize: 18 }}
                  />
                  <Typography
                    sx={{ fontSize: '0.85rem', color: 'text.secondary' }}
                  >
                    Folha auditada e aprovada para pagamento.
                  </Typography>
                </Box>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Divider />

      {/* CTA Section */}
      <Container
        sx={{
          py: { xs: 8, md: 12 },
          maxWidth: '700px !important',
          textAlign: 'center',
        }}
      >
        <Typography
          variant="h2"
          sx={{
            fontSize: { xs: '1.75rem', md: '2.25rem' },
            fontWeight: 700,
            mb: 2,
          }}
        >
          Pronto para eliminar as planilhas?
        </Typography>
        <Typography
          sx={{
            color: 'text.secondary',
            fontSize: '1rem',
            mb: 4,
            lineHeight: 1.7,
          }}
        >
          Solicite acesso e comece a automatizar a sua folha de pagamento PJ em
          minutos.
        </Typography>
        <Button
          variant="contained"
          size="large"
          onClick={() => navigate('/register')}
          sx={{ fontWeight: 600, px: 5, py: 1.5 }}
        >
          Criar Minha Conta
        </Button>
      </Container>

      {/* Footer */}
      <Box
        sx={{
          borderTop: 1,
          borderColor: 'divider',
          py: 4,
          bgcolor: 'background.paper',
        }}
      >
        <Container sx={{ maxWidth: '1100px !important' }}>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: 2,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box
                sx={{
                  width: 20,
                  height: 20,
                  bgcolor: 'primary.main',
                  borderRadius: 0.5,
                }}
              />
              <Typography variant="body2" fontWeight={600}>
                Payroll System
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 4 }}>
              {[
                { label: 'Recursos', href: '#recursos' },
                { label: 'Como Funciona', href: '#fluxo' },
              ].map((link) => (
                <Typography
                  key={link.label}
                  component="a"
                  href={link.href}
                  sx={{
                    color: 'text.secondary',
                    textDecoration: 'none',
                    fontSize: '0.85rem',
                    '&:hover': { color: 'primary.main' },
                  }}
                >
                  {link.label}
                </Typography>
              ))}
            </Box>

            <Typography
              variant="body2"
              sx={{ color: 'text.secondary', fontSize: '0.8rem' }}
            >
              &copy; 2026 Payroll System. Todos os direitos reservados.
            </Typography>
          </Box>
        </Container>
      </Box>
    </Box>
  )
}
