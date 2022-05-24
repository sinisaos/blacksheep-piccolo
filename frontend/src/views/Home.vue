<template>
    <div class="container">
        <div class="row row-cols-1 row-cols-md-3 g-2">
            <div v-for="(task, index) in tasks" :key="index">
                <div class="card p-2 mb-4 rounded">
                    <div class="card-body">
                        <p class="mb-0">
                            Posted by
                            <span
                                ><b>{{ task.readable }}</b>
                                <vue-moments-ago
                                    prefix=""
                                    suffix="ago"
                                    :date="task.created_at"
                                ></vue-moments-ago
                            ></span>
                        </p>
                        <h2>
                            {{ task.name }}
                        </h2>
                        <p class="mb-0">Completed - {{ task.completed }}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-12">
                <button
                    @click="getPrevTasks"
                    class="btn btn-info"
                    style="display: none"
                    v-if="tasks[0]['id'] == firstRow"
                >
                    Previous
                </button>
                <button
                    @click="getPrevTasks"
                    class="btn btn-outline-info"
                    v-else
                >
                    Previous
                </button>
                &nbsp;
                <button
                    @click="getTasks"
                    class="btn btn-outline-info"
                    v-if="tasks[tasks.length - 1]['id'] != lastRow"
                >
                    Next
                </button>
            </div>
        </div>
    </div>
</template>
<script>
import axios from "axios"
import VueMomentsAgo from "vue-moments-ago"

export default {
    data() {
        return {
            tasks: [],
            cursor: "",
            firstRow: "",
            lastRow: ""
        }
    },
    components: {
        VueMomentsAgo
    },
    computed: {
        isLoggedIn() {
            return this.$store.getters.isAuthenticated
        }
    },
    methods: {
        async getTasks() {
            let response = await axios.get("/api/tasks?cursor=" + this.cursor)
            this.tasks = response.data.rows
            this.cursor = response.headers["next_cursor"]
            this.firstRow = parseInt(response.headers["first_row"])
            this.lastRow = parseInt(response.headers["last_row"])
            return this.tasks
        },
        async getPrevTasks() {
            let response = await axios.get(
                "/api/tasks?cursor=" + this.cursor + "&previous=yes"
            )
            this.tasks = response.data.rows
            this.cursor = response.headers["next_cursor"]
            return this.tasks
        }
    },
    mounted() {
        this.getTasks()
    }
}
</script>

<style lang="less" scoped>
.vue-moments-ago {
    font-size: 1rem;
}
</style>
