# 字型授權

`HanWangHeiHeavy-subset.woff2` 為「王漢宗特黑體繁」（HanWangHeiHeavy, wt014.ttf）之子集，
只保留網站各頁用到的字元。全站（首頁、科目頁、各章講義）都使用這個字型。

- 原作者：王漢宗教授（中原大學數學系）
- 授權：GNU General Public License v2
- 原始檔：https://code.google.com/archive/p/wangfonts/downloads

新增或修改頁面文字後，執行 `python3 tools/build-font.py <wt014.ttf 路徑>` 重新產生子集，
否則新加入的字會改用備用字型顯示。
