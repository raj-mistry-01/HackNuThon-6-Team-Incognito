const  test_status = async (req , res) => {
    const resp = await fetch("https://e69b-2401-4900-7903-cc20-953f-8402-1893-c973.ngrok-free.app/test-status")
    const json_ = resp.json()
    console.log(json_)
    return res.status(201).json({ok : "ok"})
}
export { test_status}