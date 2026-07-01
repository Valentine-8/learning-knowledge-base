# Repository migration script - UTF-8
$ErrorActionPreference = "Stop"
$root = "d:\学习"
Set-Location $root

function Ensure-Dir($path) {
    if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path -Force | Out-Null }
}

function Move-ItemSafe([string]$src, [string]$dst) {
    if (-not (Test-Path -LiteralPath $src)) { return }
    $dstDir = Split-Path -LiteralPath $dst -Parent
    if ($dstDir) { Ensure-Dir $dstDir }
    if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force -Recurse -ErrorAction SilentlyContinue }
    git mv -- "$src" "$dst" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Move-Item -LiteralPath $src -Destination $dst -Force
    }
}

function Copy-ItemSafe([string]$src, [string]$dst) {
    if (-not (Test-Path -LiteralPath $src)) { return }
    $dstDir = Split-Path -LiteralPath $dst -Parent
    if ($dstDir) { Ensure-Dir $dstDir }
    Copy-Item -LiteralPath $src -Destination $dst -Force
}

function Move-Files([string]$srcDir, [string]$dstDir) {
    if (-not (Test-Path -LiteralPath $srcDir)) { return }
    Ensure-Dir $dstDir
    Get-ChildItem -LiteralPath $srcDir -File | ForEach-Object {
        Move-ItemSafe (Join-Path $srcDir $_.Name) (Join-Path $dstDir $_.Name)
    }
}

Write-Host "Creating skeleton..."
$dirs = @(
    "00-Governance/03-Learning-Roadmaps",
    "01-Java/02-面向对象", "01-Java/03-集合框架", "01-Java/06-注解与反射", "01-Java/07-IO与NIO", "01-Java/08-Lambda与Stream",
    "02-Spring-Ecosystem/01-Spring-Framework",
    "03-Database/01-数据库基础", "03-Database/02-MySQL",
    "04-Redis", "05-Message-Queue", "06-Middleware/01-Elasticsearch",
    "08-JVM/01-JVM基础", "09-Concurrency/01-并发基础",
    "10-Distributed-Systems/01-分布式基础", "11-Architecture/01-架构基础", "15-DevOps/01-Git与协作",
    "16-Computer-Science/01-算法与数据结构", "16-Computer-Science/02-计算机网络", "16-Computer-Science/03-操作系统", "16-Computer-Science/04-安全",
    "18-AI-Engineering", "19-Cpp/01-语言与嵌入式", "19-Cpp/02-笔记",
    "21-Interview/01-面试方法论", "21-Interview/02-Java面试", "21-Interview/04-架构面试", "21-Interview/05-项目面试", "21-Interview/06-简历与求职",
    "90-Growth/01-学习方法", "90-Growth/02-工程素养", "90-Growth/03-职业发展", "90-Growth/04-个人模板",
    "98-Personal-Topics/Photography", "99-Archive/Frontend-Demos/Vue2-Basic", "99-Archive/Old-Roadmaps", "99-Archive/Legacy-Technical-Growth",
    "assets/images", "assets/diagrams", "assets/screenshots", "assets/examples",
    "07-Microservices", "12-Linux", "13-Docker", "14-Kubernetes", "17-Frontend", "20-Project-Practice"
)
foreach ($d in $dirs) { Ensure-Dir $d }

Write-Host "Migrating data middleware..."
Move-Files "技术成长\数据与中间件\MySQL" "03-Database\02-MySQL"
Move-Files "技术成长\数据与中间件\Redis" "04-Redis"
Move-Files "技术成长\数据与中间件\消息队列" "05-Message-Queue"
Move-Files "技术成长\数据与中间件\Elasticsearch" "06-Middleware\01-Elasticsearch"

Write-Host "Migrating computer science..."
Move-Files "技术成长\计算机基础\算法与数据结构" "16-Computer-Science\01-算法与数据结构"
Move-Files "技术成长\计算机基础\计算机网络" "16-Computer-Science\02-计算机网络"
Move-Files "技术成长\计算机基础\操作系统" "16-Computer-Science\03-操作系统"
Move-Files "技术成长\计算机基础\安全" "16-Computer-Science\04-安全"

Write-Host "Migrating AI..."
Move-Files "技术成长\AI工程" "18-AI-Engineering"

Write-Host "Migrating Java..."
Move-Files "技术成长\Java\笔记\phase1-集合" "01-Java\03-集合框架"
Move-ItemSafe "技术成长\Java\笔记\Java语言与IO\01-面向对象与泛型.md" "01-Java\02-面向对象\01-面向对象与泛型.md"
Move-ItemSafe "技术成长\Java\笔记\Java语言与IO\02-注解反射与异常.md" "01-Java\06-注解与反射\02-注解反射与异常.md"
Move-ItemSafe "技术成长\Java\笔记\Java语言与IO\03-BIO-NIO与Netty.md" "01-Java\07-IO与NIO\03-BIO-NIO与Netty.md"
Move-ItemSafe "技术成长\Java\笔记\Java语言与IO\04-Stream与新特性.md" "01-Java\08-Lambda与Stream\04-Stream与新特性.md"
Move-ItemSafe "技术成长\Java\笔记\Java语言与IO\05-面试题库与案例.md" "01-Java\02-面向对象\05-Java语言面试题库.md"
Move-ItemSafe "技术成长\Java\笔记\Java语言与IO\README.md" "01-Java\07-IO与NIO\README-Java语言与IO.md"

Move-ItemSafe "技术成长\Java\笔记\phase2-JVM\00-复习手册.md" "08-JVM\01-JVM基础\00-复习手册汇总.md"
Move-ItemSafe "技术成长\Java\笔记\phase2-JVM\README.md" "08-JVM\01-JVM基础\README-phase2.md"
Move-ItemSafe "技术成长\Java\笔记\phase3-并发\00-复习手册.md" "09-Concurrency\01-并发基础\00-复习手册汇总.md"
Move-ItemSafe "技术成长\Java\笔记\phase3-并发\README.md" "09-Concurrency\01-并发基础\README-phase3.md"
Move-ItemSafe "技术成长\Java\笔记\phase4-Spring\00-复习手册.md" "02-Spring-Ecosystem\01-Spring-Framework\00-复习手册汇总.md"
Move-ItemSafe "技术成长\Java\笔记\phase4-Spring\README.md" "02-Spring-Ecosystem\01-Spring-Framework\README-phase4.md"
Move-ItemSafe "技术成长\Java\笔记\phase5-数据库\00-复习手册.md" "03-Database\01-数据库基础\00-复习手册汇总.md"
Move-ItemSafe "技术成长\Java\笔记\phase5-数据库\README.md" "03-Database\01-数据库基础\README-phase5.md"
Move-ItemSafe "技术成长\Java\笔记\phase6-分布式\00-复习手册.md" "10-Distributed-Systems\01-分布式基础\00-复习手册汇总.md"
Move-ItemSafe "技术成长\Java\笔记\phase6-分布式\README.md" "10-Distributed-Systems\01-分布式基础\README-phase6.md"
Move-ItemSafe "技术成长\Java\笔记\phase7-架构\00-复习手册.md" "11-Architecture\01-架构基础\00-复习手册汇总.md"
Move-ItemSafe "技术成长\Java\笔记\phase7-架构\README.md" "11-Architecture\01-架构基础\README-phase7.md"
Move-ItemSafe "技术成长\Java\笔记\phase8-DevOps\00-复习手册.md" "15-DevOps\01-Git与协作\00-复习手册汇总.md"
Move-ItemSafe "技术成长\Java\笔记\phase8-DevOps\README.md" "15-DevOps\01-Git与协作\README-phase8.md"

Move-ItemSafe "技术成长\Java\02-7年工程师技能全景索引.md" "00-Governance\03-Learning-Roadmaps\07-技能全景索引.md"
Move-ItemSafe "技术成长\Java\01-7年Java工程师技能清单.md" "00-Governance\03-Learning-Roadmaps\08-技能清单.md"
Move-ItemSafe "技术成长\Java\03-7年Java工程师学习路线.md" "00-Governance\03-Learning-Roadmaps\01-Java-Backend-Roadmap.md"
Move-ItemSafe "技术成长\Java\04-java学习.md" "01-Java\00-学习导航.md"
Move-ItemSafe "技术成长\Java\06-项目经历面试手册.md" "21-Interview\05-项目面试\01-06-项目经历面试手册.md"
Move-ItemSafe "技术成长\Java\07-面试题大全Q&A.md" "21-Interview\02-Java面试\06-07-面试题大全Q&A.md"
Move-ItemSafe "技术成长\Java\08-面试前速查.md" "21-Interview\02-Java面试\07-08-面试前速查.md"
Move-ItemSafe "技术成长\Java\09-系统设计练手.md" "21-Interview\04-架构面试\05-09-系统设计练手.md"
Move-ItemSafe "技术成长\Java\05-简历.md" "21-Interview\06-简历与求职\06-简历-Java.md"
Move-ItemSafe "技术成长\01-扩展技能全景.md" "00-Governance\03-Learning-Roadmaps\09-01-扩展技能全景.md"

Write-Host "Migrating C++..."
Get-ChildItem -LiteralPath "技术成长\C++嵌入式" -File -ErrorAction SilentlyContinue | ForEach-Object {
    $n = $_.Name
    if ($n -match "简历|面试|公司|岗位") {
        Move-ItemSafe "技术成长\C++嵌入式\$n" "21-Interview\06-简历与求职\$n"
    } else {
        Move-ItemSafe "技术成长\C++嵌入式\$n" "19-Cpp\01-语言与嵌入式\$n"
    }
}
Move-ItemSafe "技术成长\C++嵌入式\notes" "19-Cpp\02-笔记"

Write-Host "Migrating growth..."
Move-ItemSafe "技术成长\00-通用\11-工程素养-00-复习手册.md" "90-Growth\02-工程素养\01-工程素养00-复习手册.md"
Move-ItemSafe "技术成长\00-通用\01-阅读指南.md" "90-Growth\01-学习方法\01-阅读指南.md"
Move-ItemSafe "技术成长\00-通用\03-学习进度追踪.md" "90-Growth\01-学习方法\06-03-学习进度追踪.md"
Move-ItemSafe "技术成长\00-通用\04-个人基线评估.md" "90-Growth\01-学习方法\07-04-个人基线评估.md"
Move-ItemSafe "技术成长\00-通用\02-统一主路线.md" "90-Growth\01-学习方法\08-02-统一主路线.md"
Move-ItemSafe "技术成长\00-通用\05-错题与易忘概念.md" "90-Growth\01-学习方法\09-05-错题与易忘概念.md"
Move-ItemSafe "技术成长\00-通用\06-算法刷题记录.md" "90-Growth\01-学习方法\10-06-算法刷题记录.md"
Move-ItemSafe "技术成长\00-通用\07-Cursor操作手册.md" "90-Growth\01-学习方法\11-07-Cursor操作手册.md"
Move-ItemSafe "技术成长\00-通用\12-项目实战清单.md" "90-Growth\03-职业发展\06-12-项目实战清单.md"
Move-ItemSafe "技术成长\00-通用\13-周复盘模板.md" "90-Growth\04-个人模板\01-13-周复盘模板.md"
Move-ItemSafe "技术成长\00-通用\08-资源书签.md" "90-Growth\01-学习方法\12-08-资源书签.md"
Move-ItemSafe "技术成长\00-通用\09-求职追踪.md" "21-Interview\06-简历与求职\04-09-求职追踪.md"
Move-ItemSafe "技术成长\00-通用\10-面试与晋升素材库.md" "21-Interview\01-面试方法论\06-10-面试与晋升素材库.md"
Move-Files "技术成长\00-通用\archive" "99-Archive\Old-Roadmaps"
Move-ItemSafe "技术成长\00-通用\reviews" "90-Growth\05-周复盘记录"

Write-Host "Migrating personal & archive..."
Move-ItemSafe "奥林巴斯ep7\EP7-Guide" "98-Personal-Topics\Photography\Olympus-EP7"
Move-ItemSafe "奥林巴斯ep7\.vscode" "98-Personal-Topics\Photography\.vscode"
Move-ItemSafe "奥林巴斯ep7\md-preview-light.css" "98-Personal-Topics\Photography\md-preview-light.css"
if (Test-Path -LiteralPath "前端\vue") {
    Get-ChildItem -LiteralPath "前端\vue" | ForEach-Object {
        Move-ItemSafe "前端\vue\$($_.Name)" "99-Archive\Frontend-Demos\Vue2-Basic\$($_.Name)"
    }
}

Write-Host "Archiving legacy..."
Move-ItemSafe "技术成长" "99-Archive\Legacy-Technical-Growth\技术成长"

Copy-ItemSafe "Repository-Specification.md" "00-Governance\01-Repository-Specification.md"
Copy-ItemSafe "Repository-Structure.md" "00-Governance\02-Repository-Structure.md"

Write-Host "Done."
