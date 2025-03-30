import  express from 'express';
import cors from "cors";
import cookieParser from "cookie-parser";
import testRouter from "./Routes/expr.routes.js"
import userRouter from "./Routes/users.routes.js"
const app = express();

app.use(
  cors({
    origin: "*", 
  })
);

app.use(express.json({ limit: "16kb" }));
app.use(express.urlencoded({ extended: true, limit: "16kb" }));
app.use(express.static("public"));
app.use(cookieParser());
app.use(express.json());

app.use("/api/test1/exprs" , testRouter)
app.use("/api/users" , userRouter)
app.get("/api/testing", (req, res) => {
  return res.json({"ok" : "ok"})
});


export {app}
