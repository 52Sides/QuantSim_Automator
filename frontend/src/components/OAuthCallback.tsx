import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import useAuthStore from "../store/auth";

export default function OAuthCallback() {
  const location = useLocation();
  const navigate = useNavigate();
  const setTokens = useAuthStore((s) => s.setTokens);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const access = params.get("access_token");
    const refresh = params.get("refresh_token");

    if (access && refresh) {
      setTokens({ access, refresh });
      navigate("/dashboard");
    } else {
      navigate("/login");
    }
  }, [location, navigate]);

  return <p className="text-center mt-8">Logging in with Google...</p>;
}
