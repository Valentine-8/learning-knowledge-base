# vue学习笔记

[TOC]

## 简介

VUE：一套用于构建用户界面的【渐进式】（自底向上逐层的应用）JavaScript框架。

**特点**：

* 组件化模式
* 声明式编码，编码人员无需直接操作DOM

### 初识VUE

1. 想让Vue工作，就必须创建一个Vue实例，且要传入一个配置对象;  
2. root容器里的代码依然符合html规范，只不过混入了一些特殊的Vue语法;  
3. root容器里的代码被称为【Vue模板】；  
4. Vue实例和容器是一对一的；  
5. 真实开发中只有一个Vue实例，并且会配合着组件一起使用;  
6. {{xxx}}中的xxx要写js表达式，且xxx可以自动读取到data中的所有属性；  
7. 一旦data中的数据发生改变，那么页面中用到该数据的地方也会自动更新；

注意区分: js表达式 和 js代码(语句)    

1.表达式:  
一个表达式会产生一个值，可以放在任何一个需要值的地方:  
(1).a  
(2).a+b  
(3).demo(1)  
(4).x === y ?'a':b  

2.js代码(语句)  
(1).if(){}  
(2). for(){}

``` html
<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>helloworld</title>
    <!-- 引入vue-->
    <script type="text/javascript" src="../js/vue.js"></script>
</head>

<body>
    <div id="root">
        <h1> hello {{name}}</h1>
    </div>
    <script type="text/javascript">
        Vue.config.productionTip = false
        //创建实例
        new Vue({
            el:'#root',   //el用于指定当前Vue实例为哪个容器服务，值通常为css选择器字符串。
            data:{  //数据仅供el指定容器使用
                name:'messi'
            }
        })
    </script>
</body>
</html> 
```

### VUE模板语法

#### 1.插值语法

功能：用于解析标签体内容
写法：{{xxx}}，xxxx是js表达式，可以直接读取data里的内容

#### 2.指令语法

功能：用于解析标签（包括 标签属性、标签体内容、绑定事件。。。）
举例：v-bind:href="xxx"简写 :href="xxx"  ,xxx会被当成js表达式， 还有v-if等v-开头的指令

### 数据绑定

#### v-bind（单向绑定）

简写做：xxx，数据只能从data流向页面

#### v-model（双向绑定）

双向绑定，只能用于表单类元素
v-model:value="xxxxx" ,可以直接写作 v-model="xxxxx" , 数据可以从data流向页面也可以从页面流向model

#### el的两种写法

1. Vue内部声明

``` html
    <script type="text/javascript">
        new Vue({
            el:'#root'   
        })
    </script>
```

2. 调用实例v的缔造者原型对象上的$mount方法挂载到容器,**记住#**

``` html
    <script type="text/javascript">
        const v = new Vue({
        })
        v.$mount('#root')
    </script>
```

#### data的两种写法

1.对象式

``` html

    <script type="text/javascript">
        new Vue({
            el:'#root',  
            data:{  
                name:'messi'
            }
        })
    </script>
```

2.函数式,以后搞了组件必须得用函数式
**data函数不能写成data:()=>{}箭头函数，必须普通函数,不然this变window，Vue所管理的都是**

``` html

    <script type="text/javascript">
        new Vue({
            el:'#root',  
            //必须返回一个对象
            data:function(){  
                console.log(' this ====> ',this) //此处this是Vue实例对象
                return {
                    name:'messi'
                    }
            }
        })
    </script>
```

### MVVM模型

1. **M**：Model ，模型，对应data里的数据
2. **V**：View，视图，对应模板
3. **VM**：ViewModel ，视图模型，对应Vue实例对象
4. **发现**：vm上所有的属性，以及Vue原型所有的属性，都可以在Vue模板中使用
![模型图](./屏幕截图%202023-10-12%20235456.png)

### 数据代理

#### 回顾object.defineproperty方法

```javascript
let number = 26;
        let person = {
            name:"zhangsan",
            xingbie:"man"
        }
        //defineProperty方法加进去的属性默认是不能枚举或者说被遍历的
        Object.defineProperty(person,'age',{
            //value:18,
            //enumerable:true,  //控制属性是否可以枚举
            //writable:true,  //控制属性能否被覆盖
            //configurable:true,  ///控制属性能否被删除
            //当有人读取person的age属性时，才会调用getter
            get:function(){
                return number
            },

            set(value){
                number = value
            }
        })

        for (const key in person) {
            if (Object.hasOwnProperty.call(person, key)) {
                const element = person[key];
                //console.log(element)
            }
        }
        console.log(person)
```

#### Vue中的数据代理

**数据代理**：通过一个对象，代理对另一个对象中的属性的操作（WR）

Vue做的数据代理就是把vm中data里的数据用defineProperty放了一份在vm中，并且为每个属性加一个getter和setter；为了方便在模板中读数据，不用{{_data.name}}

### 事件处理

#### 事件的基本使用

1. 用v-on：xxx或者@xxx绑定事件，其中xxx是事件名
2. 事件的回调都需要配置在methods对象中，最终都会出现在vm上
3. methods中的函数不要写箭头函数，否则this是window而不是vm（或组件实例对象？）
4. ```@click```和```@click($event)```是一样的

```html
 <button @click="showinfo2($event,66)">点我弹窗</button>
```

```javascript
 const vm = new Vue({
            data:function(){  
                return {
                    name:'哈哈哈'
                }
            },
            methods:{
                showinfo(event){
                    alert(event)
                    console.log(event)
                },
                showinfo2(event,num){
                    alert(num)
                    console.log(event)
                }
            }
        })
```

#### 事件修饰符

Vue中的事件修饰符

1. **prevent**  阻止默认事件
2. **stop** 阻止冒泡
3. **once** 只触发一次事件
4. **capture** 使用事件的捕获模式
5. **self** 只有event.target是当前操作元素时才触发事件
6. **passive** 事件的默认行为立即执行，无需等待事件回调完毕
修饰符是可以连着写的
**@click.stop.prevent** 先阻止冒泡，再阻止默认事件。

#### 键盘事件

**1.Vue中常见的按键别名**
1. 回车 enter
2. 删除 delete
3. 空格 space
4. 换行 tab

**2.Vue中未提供别名的按键处理**：
可以通过按键原始的key值进行绑定，但是要注意转为kabab-case（短横线命名）
**3.系统修饰符（用法特殊）**
ctrl，alt，shift，meta
1. 配合keyup使用，按下修饰键同时，按下其他键，释放其他键，事件会被触发。
2. 配合keydown使用，正常触发。
3. 后面可以再接一个 ，**keyup.ctrl.y**，只有ctrl+y可以触发

**4.也可以使用keyCode去指定具体按键**
（不推荐
**5.Vue.config.keyCodes.自定义键名 = 键码** 
可以定制按键别名。