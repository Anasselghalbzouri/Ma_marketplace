<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('categories', function (Blueprint $table) {
            $table->id();
            $table->string('name', 100)->nullable(false);
            $table->boolean('is_return_excluded')->nullable(false)->default(false);
            $table->timestamps();
            $table->unique('name');
        });

    }

    public function down(): void
    {
        Schema::dropIfExists('categories');
    }
};
