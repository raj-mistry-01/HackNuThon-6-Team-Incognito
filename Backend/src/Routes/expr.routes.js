import { Router } from "express";
import {sendexpr} from "../Controllers/Expr.controller.js"
const router = Router();
router.route("/addexpr").post(sendexpr)
export default router;