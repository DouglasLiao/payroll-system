import { CssBaseline, ThemeProvider, GlobalStyles } from "@mui/material";
import { getTheme } from "@payroll/design-system";
import LandingPage from "./components/LandingPage";
import "@fontsource/outfit/300.css";
import "@fontsource/outfit/400.css";
import "@fontsource/outfit/500.css";
import "@fontsource/outfit/600.css";
import "@fontsource/outfit/700.css";

function App() {
  const landingTheme = getTheme("dark");

  return (
    <ThemeProvider theme={landingTheme}>
      <CssBaseline />
      <GlobalStyles
        styles={{
          "#root": {
            display: "flex",
            flexDirection: "column",
            minHeight: "100vh",
            width: "100%",
          },
        }}
      />
      <LandingPage />
    </ThemeProvider>
  );
}

export default App;
