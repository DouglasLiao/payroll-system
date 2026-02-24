import {
  Box,
  Button,
  Container,
  Typography,
  Grid,
  CardContent,
  alpha,
  useTheme,
  Card,
} from "@mui/material";
import { keyframes } from "@emotion/react";
import BoltIcon from "@mui/icons-material/Bolt";
import BusinessIcon from "@mui/icons-material/Business";
import NoteAltIcon from "@mui/icons-material/NoteAlt";
import EmailIcon from "@mui/icons-material/Email";
import { useState } from "react";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import dashboardPreview from "../assets/dashboard-preview.png";

const float = keyframes`
  0% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
  100% { transform: translateY(0px); }
`;

export default function LandingPage() {
  const theme = useTheme();

  // Use theme colors directly instead of hardcoded strings
  const bgColor = theme.palette.background.default;
  const textPrimary = theme.palette.text.primary;
  const textSecondary = theme.palette.text.secondary;
  const accent = theme.palette.primary.main;
  const accentLight = theme.palette.primary.light;

  const pulse = keyframes`
    0% { box-shadow: 0 0 0 0 ${alpha(accent, 0.4)}; }
    70% { box-shadow: 0 0 0 15px ${alpha(accent, 0)}; }
    100% { box-shadow: 0 0 0 0 ${alpha(accent, 0)}; }
  `;

  const [comingSoonOpen, setComingSoonOpen] = useState(false);

  const handleComingSoon = (e?: React.MouseEvent) => {
    if (e) e.preventDefault();
    setComingSoonOpen(true);
  };

  return (
    <Box
      sx={{
        backgroundColor: bgColor,
        color: textPrimary,
        minHeight: "100vh",
        width: "100%",
        display: "flex",
        flexDirection: "column",
        fontFamily: "'Outfit', 'Inter', sans-serif",
        overflowX: "hidden",
      }}
    >
      {/* Navigation */}
      <Box
        component="nav"
        sx={{
          position: "fixed",
          top: 0,
          width: "100%",
          zIndex: 100,
          background: alpha(theme.palette.background.default, 0.8),
          backdropFilter: "blur(20px)",
          borderBottom: `1px solid ${theme.palette.divider}`,
          py: 2,
          px: { xs: 2, md: 5 },
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Box
            sx={{
              width: 24,
              height: 24,
              background: `linear-gradient(135deg, ${theme.palette.secondary.main} 0%, ${theme.palette.primary.main} 100%)`,
              borderRadius: 1.5,
            }}
          />
          <Typography
            variant="h6"
            fontWeight={700}
            sx={{ letterSpacing: -0.5 }}
          >
            Payroll
            <Box component="span" sx={{ color: accentLight }}>
              .
            </Box>
          </Typography>
        </Box>
        <Box sx={{ display: { xs: "none", md: "flex" }, gap: 4 }}>
          {["Recursos", "Como Funciona", "Auditoria"].map((item) => (
            <Typography
              key={item}
              component="a"
              href={
                item === "Como Funciona"
                  ? "#fluxo"
                  : item === "Recursos"
                    ? "#recursos"
                    : "#"
              }
              onClick={item === "Auditoria" ? handleComingSoon : undefined}
              sx={{
                color: textSecondary,
                textDecoration: "none",
                fontWeight: 500,
                fontSize: "0.95rem",
                cursor: "pointer",
                transition: "color 0.3s",
                "&:hover": { color: textPrimary },
              }}
            >
              {item}
            </Typography>
          ))}
        </Box>
        <Box sx={{ display: "flex", gap: 2, alignItems: "center" }}>
          <Button
            variant="text"
            href="/login"
            sx={{
              color: textPrimary,
              fontWeight: 500,
              "&:hover": { color: accentLight },
            }}
          >
            Entrar
          </Button>
          <Button
            variant="contained"
            href="/register"
            sx={{
              bgcolor: textPrimary,
              color: bgColor,
              fontWeight: 600,
              textTransform: "none",
              borderRadius: 2,
              px: 3,
              "&:hover": {
                bgcolor: theme.palette.common.white,
                boxShadow: `0 0 20px ${alpha(theme.palette.common.white, 0.3)}`,
                transform: "translateY(-2px)",
              },
              transition: "all 0.3s",
            }}
          >
            Comece Agora
          </Button>
        </Box>
      </Box>

      {/* Hero Section */}
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          pt: 16,
          pb: 8,
          px: { xs: 2, md: 5 },
          textAlign: "center",
          position: "relative",
        }}
      >
        {/* Glow Effects */}
        <Box
          sx={{
            position: "absolute",
            width: 500,
            height: 500,
            bgcolor: accent,
            filter: "blur(150px)",
            borderRadius: "50%",
            opacity: 0.4,
            zIndex: 0,
            top: -100,
            left: -100,
          }}
        />
        <Box
          sx={{
            position: "absolute",
            width: 500,
            height: 500,
            bgcolor: theme.palette.secondary.main,
            filter: "blur(150px)",
            borderRadius: "50%",
            opacity: 0.2,
            zIndex: 0,
            bottom: "10%",
            right: -200,
          }}
        />

        <Box
          sx={{
            position: "relative",
            zIndex: 10,
            maxWidth: 800,
            mx: "auto",
            mb: 8,
          }}
        >
          <Typography
            variant="h1"
            sx={{
              fontSize: { xs: "3rem", md: "4.5rem" },
              fontWeight: 700,
              lineHeight: 1.1,
              mb: 3,
              letterSpacing: -2,
            }}
          >
            A evolução da{" "}
            <Box
              component="span"
              sx={{
                background: `linear-gradient(135deg, ${theme.palette.secondary.main} 0%, ${theme.palette.primary.main} 100%)`,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              folha de pagamento PJ
            </Box>
            .
          </Typography>
          <Typography
            sx={{
              fontSize: "1.25rem",
              color: textSecondary,
              mb: 5,
              maxWidth: 600,
              mx: "auto",
            }}
          >
            Automatize o cálculo de pró-rata, vale transporte, horas extras e
            gerencie todas as suas rotinas mensais B2B sem planilhas.
          </Typography>
          <Box
            sx={{
              display: "flex",
              gap: 2,
              justifyContent: "center",
              flexWrap: "wrap",
            }}
          >
            <Button
              variant="contained"
              size="large"
              href="/register"
              sx={{
                bgcolor: textPrimary,
                color: bgColor,
                fontWeight: 600,
                textTransform: "none",
                borderRadius: 2,
                px: 4,
                py: 1.5,
                fontSize: "1.1rem",
                "&:hover": {
                  bgcolor: theme.palette.common.white,
                  boxShadow: `0 0 20px ${alpha(theme.palette.common.white, 0.3)}`,
                  transform: "translateY(-2px)",
                },
                transition: "all 0.3s",
              }}
            >
              Solicitar Acesso
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => {
                document
                  .getElementById("fluxo")
                  ?.scrollIntoView({ behavior: "smooth" });
              }}
              sx={{
                color: textPrimary,
                borderColor: alpha(theme.palette.common.white, 0.08),
                fontWeight: 600,
                textTransform: "none",
                borderRadius: 2,
                px: 4,
                py: 1.5,
                fontSize: "1.1rem",
                "&:hover": {
                  bgcolor: alpha(theme.palette.common.white, 0.05),
                  borderColor: alpha(theme.palette.common.white, 0.2),
                },
              }}
            >
              Ver como funciona
            </Button>
          </Box>

          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              gap: { xs: 4, md: 8 },
              mt: 6,
              pt: 4,
              borderTop: `1px solid ${theme.palette.divider}`,
              flexWrap: "wrap",
            }}
          >
            {[
              { value: "100%", label: "Automatizado" },
              { value: "Zero", label: "Erros de Cálculo" },
              { value: "Multi", label: "Empresas em 1 conta" },
            ].map((stat) => (
              <Box
                key={stat.label}
                sx={{ display: "flex", flexDirection: "column" }}
              >
                <Typography
                  sx={{ fontSize: "2rem", fontWeight: 700, lineHeight: 1 }}
                >
                  {stat.value}
                </Typography>
                <Typography
                  sx={{
                    fontSize: "0.85rem",
                    color: textSecondary,
                    mt: 1,
                    textTransform: "uppercase",
                    letterSpacing: 1,
                  }}
                >
                  {stat.label}
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>

        {/* Mockup Visualization */}
        <Box
          sx={{
            width: "100%",
            maxWidth: 1000,
            position: "relative",
            zIndex: 10,
          }}
        >
          <Box
            sx={{
              position: "absolute",
              top: -50,
              right: -50,
              width: 200,
              height: 200,
              background: `linear-gradient(135deg, ${alpha(theme.palette.common.white, 0.1)}, ${alpha(theme.palette.common.white, 0)})`,
              backdropFilter: "blur(20px)",
              borderRadius: "50%",
              border: `1px solid ${alpha(theme.palette.common.white, 0.2)}`,
              animation: `${float} 6s ease-in-out infinite`,
              zIndex: 11,
            }}
          />
          <Box
            sx={{
              bgcolor: theme.palette.background.paper,
              borderRadius: 3,
              border: `1px solid ${theme.palette.divider}`,
              boxShadow: `0 25px 50px -12px ${alpha(theme.palette.common.black, 0.5)}`,
              overflow: "hidden",
              position: "relative",
              aspectRatio: "16/10",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <Box
              sx={{
                height: 40,
                bgcolor: theme.palette.background.default,
                borderBottom: `1px solid ${theme.palette.divider}`,
                display: "flex",
                alignItems: "center",
                px: 2,
                gap: 1,
              }}
            >
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  bgcolor: theme.palette.error.main,
                }}
              />
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  bgcolor: theme.palette.warning.main,
                }}
              />
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: "50%",
                  bgcolor: theme.palette.success.main,
                }}
              />
            </Box>
            <Box
              component="img"
              src={dashboardPreview}
              alt="Dashboard Preview"
              sx={{
                width: "100%",
                height: "auto",
                display: "block",
              }}
            />
          </Box>
        </Box>
      </Box>

      {/* Features Section */}
      <Container id="recursos" sx={{ py: 12, maxWidth: "1200px !important" }}>
        <Box sx={{ textAlign: "center", mb: 8 }}>
          <Typography
            variant="h2"
            sx={{
              fontSize: { xs: "2.5rem", md: "3rem" },
              fontWeight: 700,
              mb: 2,
              letterSpacing: -1,
            }}
          >
            Criado para escalar a sua operação
          </Typography>
          <Typography sx={{ color: textSecondary, fontSize: "1.125rem" }}>
            Tudo o que você precisa em uma única plataforma financeira e de
            gestão de talentos B2B.
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {[
            {
              icon: <BoltIcon fontSize="large" />,
              title: "Motor de Cálculo Inteligente",
              desc: "Calcula instantaneamente pró-rata para admissões/demissões, horas extras e feriados locais baseado no Workalendar.",
            },
            {
              icon: <BusinessIcon fontSize="large" />,
              title: "Multi-Tenancy Avançado",
              desc: "Gerencie todos os CNPJs da sua holding ou agência através de uma única conta com permissões granulares.",
            },
            {
              icon: <NoteAltIcon fontSize="large" />,
              title: "Templates de Folha (Math Templates)",
              desc: "Evite trabalhos repetitivos. Crie templates de cálculos e aplique a todos os seus colaboradores em massa.",
            },
            {
              icon: <EmailIcon fontSize="large" />,
              title: "Disparo de Comprovantes",
              desc: "Ao aprovar os pagamentos, o sistema gera Recibos em PDF e notifica cada prestador por e-mail automaticamente.",
            },
          ].map((feat, index) => (
            <Grid size={{ xs: 12, md: 6 }} key={index}>
              <Card
                sx={{
                  bgcolor: alpha(theme.palette.common.white, 0.03),
                  border: `1px solid ${alpha(theme.palette.common.white, 0.08)}`,
                  backdropFilter: "blur(12px)",
                  borderRadius: 4,
                  p: 4,
                  height: "100%",
                  transition: "all 0.3s ease",
                  "&:hover": {
                    transform: "translateY(-5px)",
                    bgcolor: alpha(theme.palette.common.white, 0.05),
                    borderColor: alpha(accentLight, 0.3),
                  },
                }}
              >
                <CardContent sx={{ p: 0, "&:last-child": { pb: 0 } }}>
                  <Box
                    sx={{
                      width: 50,
                      height: 50,
                      borderRadius: 3,
                      bgcolor: alpha(accentLight, 0.1),
                      color: accentLight,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      mb: 3,
                      border: `1px solid ${alpha(accentLight, 0.2)}`,
                    }}
                  >
                    {feat.icon}
                  </Box>
                  <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
                    {feat.title}
                  </Typography>
                  <Typography sx={{ color: textSecondary, lineHeight: 1.6 }}>
                    {feat.desc}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Flow Section */}
      <Box
        id="fluxo"
        sx={{
          py: 12,
          bgcolor: alpha(theme.palette.common.white, 0.02),
          borderTop: `1px solid ${alpha(theme.palette.common.white, 0.05)}`,
          borderBottom: `1px solid ${alpha(theme.palette.common.white, 0.05)}`,
        }}
      >
        <Container sx={{ maxWidth: "1200px !important" }}>
          <Grid container spacing={8} alignItems="center">
            <Grid size={{ xs: 12, md: 6 }}>
              <Typography
                variant="h2"
                sx={{ fontSize: "2.5rem", fontWeight: 700, mb: 2 }}
              >
                Fluxo Transparente e Lógico
              </Typography>
              <Typography
                sx={{ color: textSecondary, mb: 6, fontSize: "1.1rem" }}
              >
                A tecnologia cuidando da burocracia. Do onboarding do fornecedor
                à liquidação do pagamento.
              </Typography>

              <Box sx={{ display: "flex", flexDirection: "column", gap: 4 }}>
                {[
                  {
                    num: 1,
                    title: "Setup de Contrato",
                    desc: "Defina honorários, se ele recebe Vale Transporte, dias úteis no mês (Comercial vs Fixo de 30) e método de recebimento.",
                  },
                  {
                    num: 2,
                    title: "Aplicação de Variáveis",
                    desc: "Lance horas extras, descontos ou faltas. Os cálculos são processados on-the-fly pelo backend.",
                  },
                  {
                    num: 3,
                    title: "Auditoria IA e Pagamento",
                    desc: "Nosso agente audita os totais antes de você fechar a folha. Sem surpresas.",
                  },
                ].map((step) => (
                  <Box key={step.num} sx={{ display: "flex", gap: 3 }}>
                    <Box
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: "50%",
                        background: `linear-gradient(135deg, ${theme.palette.secondary.main} 0%, ${theme.palette.primary.main} 100%)`,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontWeight: 700,
                        flexShrink: 0,
                      }}
                    >
                      {step.num}
                    </Box>
                    <Box>
                      <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                        {step.title}
                      </Typography>
                      <Typography
                        sx={{ color: textSecondary, fontSize: "0.95rem" }}
                      >
                        {step.desc}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  gap: 2,
                }}
              >
                <Box
                  sx={{
                    px: 6,
                    py: 3,
                    bgcolor: theme.palette.background.paper,
                    borderRadius: 2,
                    border: `1px solid ${theme.palette.divider}`,
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: 1,
                    fontSize: "0.85rem",
                  }}
                >
                  Contrato
                </Box>
                <Box
                  sx={{
                    width: 2,
                    height: 40,
                    background: `linear-gradient(to bottom, ${theme.palette.divider}, ${alpha(accent, 0.5)})`,
                  }}
                />
                <Box
                  sx={{
                    px: 6,
                    py: 3,
                    bgcolor: accent,
                    borderRadius: 2,
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: 1,
                    fontSize: "0.85rem",
                    animation: `${pulse} 2s infinite`,
                    boxShadow: `0 0 20px ${alpha(accent, 0.4)}`,
                  }}
                >
                  Cálculo
                </Box>
                <Box
                  sx={{
                    width: 2,
                    height: 40,
                    background: `linear-gradient(to bottom, ${alpha(accent, 0.5)}, ${theme.palette.divider})`,
                  }}
                />
                <Box
                  sx={{
                    px: 6,
                    py: 3,
                    bgcolor: theme.palette.background.paper,
                    borderRadius: 2,
                    border: `1px solid ${theme.palette.divider}`,
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: 1,
                    fontSize: "0.85rem",
                  }}
                >
                  Pagamento
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box sx={{ py: 16, textAlign: "center", position: "relative" }}>
        <Box
          sx={{
            position: "absolute",
            width: 500,
            height: 500,
            bgcolor: theme.palette.info.light,
            filter: "blur(150px)",
            borderRadius: "50%",
            opacity: 0.1,
            zIndex: 0,
            top: "30%",
            left: "30%",
          }}
        />
        <Container sx={{ position: "relative", zIndex: 10, maxWidth: 600 }}>
          <Typography
            variant="h2"
            sx={{ fontSize: "3rem", fontWeight: 700, mb: 3, letterSpacing: -1 }}
          >
            Pronto para revolucionar o seu financeiro?
          </Typography>
          <Typography
            sx={{ color: textSecondary, fontSize: "1.125rem", mb: 5 }}
          >
            Junte-se a dezenas de empresas inovadoras que já eliminaram as
            planilhas da sua rotina mensal.
          </Typography>
          <Button
            variant="contained"
            size="large"
            href="/register"
            sx={{
              bgcolor: textPrimary,
              color: bgColor,
              fontWeight: 600,
              textTransform: "none",
              borderRadius: 2,
              px: 4,
              py: 1.5,
              fontSize: "1.1rem",
              "&:hover": {
                bgcolor: theme.palette.common.white,
                boxShadow: `0 0 20px ${alpha(theme.palette.common.white, 0.3)}`,
                transform: "translateY(-2px)",
              },
            }}
          >
            Criar Minha Conta
          </Button>
        </Container>
      </Box>

      {/* Footer */}
      <Box
        sx={{
          borderTop: `1px solid ${theme.palette.divider}`,
          py: 8,
          bgcolor: theme.palette.background.default,
        }}
      >
        <Container sx={{ maxWidth: "1200px !important" }}>
          <Grid container spacing={4} sx={{ mb: 8 }}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}
              >
                <Box
                  sx={{
                    width: 24,
                    height: 24,
                    background: `linear-gradient(135deg, ${theme.palette.secondary.main} 0%, ${theme.palette.primary.main} 100%)`,
                    borderRadius: 1.5,
                  }}
                />
                <Typography
                  variant="h6"
                  fontWeight={700}
                  sx={{ letterSpacing: -0.5 }}
                >
                  Payroll
                  <Box component="span" sx={{ color: accentLight }}>
                    .
                  </Box>
                </Typography>
              </Box>
              <Typography
                sx={{ color: textSecondary, fontSize: "0.9rem", maxWidth: 300 }}
              >
                O futuro da gestão de pagamentos corporativos.
              </Typography>
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <Typography sx={{ fontWeight: 600, mb: 2 }}>Produto</Typography>
              <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
                {["Features", "Pricing", "Changelog"].map((link) => (
                  <Typography
                    key={link}
                    component="a"
                    href="#"
                    onClick={handleComingSoon}
                    sx={{
                      color: textSecondary,
                      textDecoration: "none",
                      fontSize: "0.9rem",
                      "&:hover": { color: textPrimary },
                    }}
                  >
                    {link}
                  </Typography>
                ))}
              </Box>
            </Grid>
            <Grid size={{ xs: 12, md: 3 }}>
              <Typography sx={{ fontWeight: 600, mb: 2 }}>Legal</Typography>
              <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
                {["Privacidade", "Termos de Uso"].map((link) => (
                  <Typography
                    key={link}
                    component="a"
                    href="#"
                    onClick={handleComingSoon}
                    sx={{
                      color: textSecondary,
                      textDecoration: "none",
                      fontSize: "0.9rem",
                      "&:hover": { color: textPrimary },
                    }}
                  >
                    {link}
                  </Typography>
                ))}
              </Box>
            </Grid>
          </Grid>
          <Box
            sx={{
              borderTop: `1px solid ${alpha(theme.palette.common.white, 0.08)}`,
              pt: 4,
              textAlign: "center",
            }}
          >
            <Typography sx={{ color: textSecondary, fontSize: "0.85rem" }}>
              &copy; 2026 Payroll System. All rights reserved.
            </Typography>
          </Box>
        </Container>
      </Box>

      {/* Coming Soon Alert */}
      <Snackbar
        open={comingSoonOpen}
        autoHideDuration={4000}
        onClose={() => setComingSoonOpen(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={() => setComingSoonOpen(false)}
          severity="info"
          variant="filled"
          sx={{ width: "100%", borderRadius: 2 }}
        >
          Página em construção! Em breve novidades.
        </Alert>
      </Snackbar>
    </Box>
  );
}
