# One entry per existing formula box. Each entry is a list of (TeX, explanatory note).
FORMULAS = {
1:[
 [(r'v_{\mathrm{avg}}=\frac{\Delta x}{\Delta t}','')],
 [(r'v=\frac{\mathrm{d}x}{\mathrm{d}t}','')],
 [(r'a_{\mathrm{avg}}=\frac{\Delta v}{\Delta t}','')],
 [(r'a=\frac{\mathrm{d}v}{\mathrm{d}t}=\frac{\mathrm{d}^{2}x}{\mathrm{d}t^{2}}','')],
 [(r'v=v_0+at','')],[(r's=v_0t+\frac{1}{2}at^2','')],[(r'v^2=v_0^2+2as','')],
 [(r'h=\frac{1}{2}gt^2',''),(r'v=gt',''),(r'v^2=2gh','')]],
2:[
 [(r'\theta=\frac{s}{r}','')],[(r'\omega_{\mathrm{avg}}=\frac{\Delta\theta}{\Delta t}','平均角速度'),(r'\omega=\frac{\mathrm{d}\theta}{\mathrm{d}t}','瞬時角速度')],
 [(r'v=\omega r','')],[(r'\alpha_{\mathrm{avg}}=\frac{\Delta\omega}{\Delta t}','平均角加速度'),(r'\alpha=\frac{\mathrm{d}\omega}{\mathrm{d}t}','瞬時角加速度')],
 [(r'a_t=\alpha r','')],[(r'\omega=\omega_0+\alpha t','')],[(r'\theta=\omega_0t+\frac{1}{2}\alpha t^2','')],[(r'\omega^2=\omega_0^2+2\alpha\theta','')],
 [(r't=\sqrt{\frac{2h}{g}}','')],[(r'x=v_0t=v_0\sqrt{\frac{2h}{g}}','')],[(r't_{\max}=\frac{v_0\sin\theta}{g}','')],
 [(r'h_{\max}=\frac{(v_0\sin\theta)^2}{2g}','')],[(r'R=\frac{v_0^2\sin(2\theta)}{g}','')],
 [(r'a_c=\frac{v^2}{r}=\omega^2r','')],[(r'F_c=\frac{mv^2}{r}=m\omega^2r','')],[(r'a=\sqrt{a_t^2+a_n^2}','')]],
3:[
 [(r'\sum F=ma',''),(r'a=\frac{\sum F}{m}','')],
 [(r'1\,\mathrm{N}=1\,\mathrm{kg}\!\cdot\!\mathrm{m}/\mathrm{s}^2',''),(r'1\,\mathrm{N}=\frac{1}{9.8}\,\mathrm{kgf}','')],
 [(r'\sum F_x=ma_x',''),(r'\sum F_y=ma_y','')],
 [(r'\sum F_t=ma_t','切線方向，改變速度大小'),(r'\sum F_n=ma_n=\frac{mv^2}{r}','法線方向，改變速度方向')],
 [(r'N-W=ma',''),(r'N=m(g+a)','升降機向上加速'),(r'N=m(g-a)','升降機向下加速')],
 [(r'a=g\sin\theta','')],[(r'F_c=\frac{mv^2}{r}=m\omega^2r',''),(r'F_c=\frac{4\pi^2mr}{T^2}','以週期表示；T 為週期')]],
4:[
 [(r'W=\mathbf{F}\cdot\Delta\mathbf{s}=F\Delta s\cos\theta','')],[(r'T=\frac{1}{2}mv^2','')],
 [(r'W_{\mathrm{total}}=\Delta T=T_2-T_1','總功等於動能變化'),(r'\Delta T=\frac{1}{2}m(v_2^2-v_1^2)','')],
 [(r'U_g=mgh','')],[(r'U_s=\frac{1}{2}kx^2','')],
 [(r'T_1+U_1+W_{\mathrm{nc}}=T_2+U_2','Wnc 為非保守力所做的功'),(r'U=U_g+U_s','總位能')],
 [(r'E=T+U=\mathrm{constant}','機械能為常數'),(r'T_1+U_1=T_2+U_2',''),(r'\frac{1}{2}mv_1^2+mgh_1=\frac{1}{2}mv_2^2+mgh_2','')],
 [(r'W_f=-fd=-\mu Nd','')],[(r'T_1+U_1-fd=T_2+U_2',''),(r'T_1+U_1=T_2+U_2+fd','等價寫法')],
 [(r'P_{\mathrm{avg}}=\frac{W}{\Delta t}','平均功率'),(r'P=\frac{\mathrm{d}W}{\mathrm{d}t}=\mathbf{F}\cdot\mathbf{v}','瞬時功率')],
 [(r'\eta=\frac{W_{\mathrm{useful}}}{W_{\mathrm{input}}}\times100\%',''),(r'\eta=\frac{P_{\mathrm{useful}}}{P_{\mathrm{input}}}\times100\%','等價寫法')]],
5:[
 [(r'\mathbf{p}=m\mathbf{v}','')],[(r'\mathbf{I}=\mathbf{F}\Delta t=\int\mathbf{F}\,\mathrm{d}t','')],
 [(r'\mathbf{I}=\Delta\mathbf{p}',''),(r'\mathbf{F}\Delta t=m(\mathbf{v}_2-\mathbf{v}_1)','')],
 [(r'x_c=\frac{m_1x_1+m_2x_2+\cdots}{m_1+m_2+\cdots}',''),(r'v_c=\frac{m_1v_1+m_2v_2+\cdots}{m_1+m_2+\cdots}','')],
 [(r'p_{\mathrm{initial}}=p_{\mathrm{final}}','初動量等於末動量'),(r'm_1v_1+m_2v_2=m_1v_1^{\prime}+m_2v_2^{\prime}','')],
 [(r'e=\frac{v_2^{\prime}-v_1^{\prime}}{v_1-v_2}','相對分離速度 ÷ 相對接近速度')],
 [(r'\mathbf{L}_O=\mathbf{r}\times\mathbf{p}=\mathbf{r}\times(m\mathbf{v})',''),(r'L_O=mrv\sin\theta','角動量的大小')],
 [(r'\tau=0\;\Longrightarrow\;L=\mathrm{constant}','角動量為常數'),(r'\mathbf{r}\times\mathbf{F}=0',''),(r'\mathbf{r}\times(m\mathbf{v})=\mathrm{constant}','')]],
6:[
 [(r'\mathbf{v}_A=\mathbf{v}_B=\mathbf{v}_c',''),(r'\mathbf{a}_A=\mathbf{a}_B=\mathbf{a}_c','')],
 [(r'v=\omega r','線速度與角速度的關係'),(r'a_t=\alpha r','切線加速度'),(r'a_n=\omega^2r','法線加速度')],
 [(r'\mathbf{v}_A=\mathbf{v}_B+\mathbf{v}_{A/B}',''),(r'\mathbf{v}_A=\mathbf{v}_B+\boldsymbol{\omega}\times\mathbf{r}_{AB}','')],
 [(r'\mathbf{v}_A=\boldsymbol{\omega}\times\mathbf{r}_{PA}','P 為瞬心'),(r'|\mathbf{v}_A|=\omega|\mathbf{r}_{PA}|','速度大小')],
 [(r'\mathbf{a}_{\mathrm{abs}}=\mathbf{a}_{\mathrm{rel}}+\mathbf{a}_{\mathrm{transport}}+\mathbf{a}_{\mathrm{Cor}}','絕對加速度＝相對＋牽連＋科氏加速度'),(r'\mathbf{a}_{\mathrm{Cor}}=2\boldsymbol{\omega}\times\mathbf{v}_{\mathrm{rel}}','科氏加速度')],
 [(r'v_r=\dot{r}','徑向速度'),(r'v_{\theta}=r\dot{\theta}','橫向速度'),(r'a_r=\ddot{r}-r\dot{\theta}^{2}','徑向加速度'),(r'a_{\theta}=r\ddot{\theta}+2\dot{r}\dot{\theta}','橫向加速度')]],
7:[
 [(r'I=\sum_i m_ir_i^2','離散質點'),(r'I=\int r^2\,\mathrm{d}m','連續體')],[(r'I=I_c+md^2','')],[(r'\sum\mathbf{F}=M\mathbf{a}_c','')],[(r'\sum\tau_c=I_c\alpha','')],
 [(r'v_c=\omega R','速度關係'),(r'a_c=\alpha R','加速度關係')],
 [(r'|f|\leq\mu_sN','無滑滾動所需摩擦力未超過最大靜摩擦力'),(r'|f|>\mu_sN','超過最大靜摩擦力時發生滑動')],
 [(r'T=T_{\mathrm{translation}}+T_{\mathrm{rotation}}','總動能＝平移動能＋轉動動能'),(r'T=\frac{1}{2}Mv_c^2+\frac{1}{2}I_c\omega^2','')]]
}
